"""
鸭鸭图 Web 后端服务
基于 Flask 实现图片/视频的编码和解码
"""
import os
import io
import tempfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

# 导入核心编解码逻辑（直接复制核心函数，避免依赖 torch）
import struct
import hashlib

WATERMARK_SKIP_W_RATIO = 0.40
WATERMARK_SKIP_H_RATIO = 0.08

def _extract_payload_with_k(arr: np.ndarray, k: int) -> bytes:
    h, w, c = arr.shape
    skip_w = int(w * WATERMARK_SKIP_W_RATIO)
    skip_h = int(h * WATERMARK_SKIP_H_RATIO)
    mask2d = np.ones((h, w), dtype=bool)
    if skip_w > 0 and skip_h > 0:
        mask2d[:skip_h, :skip_w] = False
    mask3d = np.repeat(mask2d[:, :, None], c, axis=2)
    flat = arr.reshape(-1)
    idxs = np.flatnonzero(mask3d.reshape(-1))
    vals = (flat[idxs] & ((1 << k) - 1)).astype(np.uint8)
    ub = np.unpackbits(vals, bitorder="big").reshape(-1, 8)[:, -k:]
    bits = ub.reshape(-1)
    if len(bits) < 32:
        raise ValueError("Insufficient image data. 图像数据不足")
    len_bits = bits[:32]
    length_bytes = np.packbits(len_bits, bitorder="big").tobytes()
    header_len = struct.unpack(">I", length_bytes)[0]
    total_bits = 32 + header_len * 8
    if header_len <= 0 or total_bits > len(bits):
        raise ValueError("Payload length invalid. 载荷长度异常")
    payload_bits = bits[32:32 + header_len * 8]
    return np.packbits(payload_bits, bitorder="big").tobytes()

def _generate_key_stream(password: str, salt: bytes, length: int) -> bytes:
    key_material = (password + salt.hex()).encode("utf-8")
    out = bytearray()
    counter = 0
    while len(out) < length:
        out.extend(hashlib.sha256(key_material + str(counter).encode("utf-8")).digest())
        counter += 1
    return bytes(out[:length])

def _parse_header(header: bytes, password: str):
    idx = 0
    if len(header) < 1:
        raise ValueError("Header corrupted. 文件头损坏")
    has_pwd = header[0] == 1
    idx += 1
    pwd_hash = b""
    salt = b""
    if has_pwd:
        if len(header) < idx + 32 + 16:
            raise ValueError("Header corrupted. 文件头损坏")
        pwd_hash = header[idx:idx + 32]; idx += 32
        salt = header[idx:idx + 16]; idx += 16
    if len(header) < idx + 1:
        raise ValueError("Header corrupted. 文件头损坏")
    ext_len = header[idx]; idx += 1
    if len(header) < idx + ext_len + 4:
        raise ValueError("Header corrupted. 文件头损坏")
    ext = header[idx:idx + ext_len].decode("utf-8", errors="ignore"); idx += ext_len
    data_len = struct.unpack(">I", header[idx:idx + 4])[0]; idx += 4
    data = header[idx:]
    if len(data) != data_len:
        raise ValueError("Data length mismatch. 数据长度不匹配")
    if not has_pwd:
        return data, ext
    if not password:
        raise ValueError("Password required. 需要密码")
    check_hash = hashlib.sha256((password + salt.hex()).encode("utf-8")).digest()
    if check_hash != pwd_hash:
        raise ValueError("Wrong password. 密码错误")
    ks = _generate_key_stream(password, salt, len(data))
    plain = bytes(a ^ b for a, b in zip(data, ks))
    return plain, ext

# 导入编码逻辑
import sys
sys.path.append('../SS_tools-main 2')
from duck_payload_exporter import export_duck_payload, _bytes_to_binary_image

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB 最大上传
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/encode', methods=['POST'])
def encode():
    """
    编码接口：将图片/视频隐藏到鸭子图中
    
    参数：
    - file: 上传的文件
    - password: 密码（可选）
    - title: 标题（可选）
    - compress: 压缩级别 2/6/8
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400
        
        # 获取参数
        password = request.form.get('password', '')
        title = request.form.get('title', '')
        compress = int(request.form.get('compress', 2))
        
        # 读取文件内容
        file_bytes = file.read()
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        # 如果是视频，先转为二进制图片
        if ext in ['mp4', 'avi', 'mov']:
            bin_img = _bytes_to_binary_image(file_bytes, width=512)
            with io.BytesIO() as buf:
                bin_img.save(buf, format="PNG")
                raw_bytes = buf.getvalue()
            ext = f"{ext}.binpng"
        else:
            raw_bytes = file_bytes
        
        # 生成鸭子图
        output_dir = tempfile.gettempdir()
        out_path, duck_img = export_duck_payload(
            raw_bytes=raw_bytes,
            password=password,
            ext=ext,
            compress=compress,
            title=title,
            output_dir=output_dir,
            output_name=f"duck_{os.urandom(8).hex()}.png"
        )
        
        # 返回图片
        return send_file(
            out_path,
            mimetype='image/png',
            as_attachment=True,
            download_name='duck_payload.png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decode', methods=['POST'])
def decode():
    """
    解码接口：从鸭子图中提取原始内容
    
    参数：
    - file: 鸭子图文件
    - password: 密码（可选）
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 获取密码
        password = request.form.get('password', '')
        
        # 读取鸭子图
        img = Image.open(file.stream).convert("RGB")
        arr = np.array(img).astype(np.uint8)
        
        # 尝试不同的压缩级别解码
        header = None
        raw = None
        ext = None
        last_err = None
        
        for k in (2, 6, 8):
            try:
                header = _extract_payload_with_k(arr, k)
                raw, ext = _parse_header(header, password)
                break
            except Exception as e:
                last_err = e
                continue
        
        if raw is None:
            raise last_err or RuntimeError("解码失败，可能是密码错误或文件损坏")
        
        # 标准化扩展名（去掉前导点）
        clean_ext = ext.lstrip('.')
        
        # 处理二进制图片格式（视频）
        if ext.endswith('.binpng'):
            # 从二进制图片还原视频
            temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_png.write(raw)
            temp_png.close()
            
            # 读取二进制图片并转为视频字节
            bin_img = Image.open(temp_png.name).convert("RGB")
            bin_arr = np.array(bin_img).astype(np.uint8)
            flat = bin_arr.reshape(-1, 3).reshape(-1)
            video_bytes = flat.tobytes().rstrip(b"\x00")
            
            os.unlink(temp_png.name)
            
            # 正确提取原始视频格式：例如 "mp4.binpng" -> "mp4"
            orig_ext = ext.replace('.binpng', '').lstrip('.')
            return send_file(
                io.BytesIO(video_bytes),
                mimetype=f'video/{orig_ext}',
                as_attachment=True,
                download_name=f'recovered.{orig_ext}'
            )
        elif clean_ext == 'txt':
            # 文本文件
            return send_file(
                io.BytesIO(raw),
                mimetype='text/plain',
                as_attachment=True,
                download_name='recovered.txt'
            )
        elif clean_ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
            # 图片文件
            return send_file(
                io.BytesIO(raw),
                mimetype=f'image/{clean_ext}',
                as_attachment=True,
                download_name=f'recovered.{clean_ext}'
            )
        else:
            # 其他文件
            return send_file(
                io.BytesIO(raw),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=f'recovered.{clean_ext}'
            )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'version': '1.2'})

@app.route('/api/merge-videos', methods=['POST'])
def merge_videos():
    """
    合并多个视频
    
    参数：
    - files: 多个视频文件（按顺序）
    """
    try:
        # 检查是否有文件
        if 'files' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        files = request.files.getlist('files')
        if len(files) < 2:
            return jsonify({'error': '至少需要2个视频文件'}), 400
        
        # 保存临时文件
        temp_files = []
        for i, file in enumerate(files):
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            file.save(temp_file.name)
            temp_files.append(temp_file.name)
        
        # 创建文件列表
        list_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for temp_file in temp_files:
            list_file.write(f"file '{temp_file}'\n")
        list_file.close()
        
        # 输出文件
        output_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        output_file.close()
        
        # 使用 ffmpeg 合并
        import subprocess
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file.name,
            '-c', 'copy',
            output_file.name,
            '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 清理临时文件
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        try:
            os.unlink(list_file.name)
        except:
            pass
        
        if result.returncode != 0:
            try:
                os.unlink(output_file.name)
            except:
                pass
            return jsonify({'error': f'FFmpeg 错误: {result.stderr}'}), 500
        
        # 返回合并后的视频
        return send_file(
            output_file.name,
            mimetype='video/mp4',
            as_attachment=True,
            download_name='merged_video.mp4'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch-image', methods=['POST'])
def fetch_image():
    """
    从 URL 获取图片（代理接口，避免跨域）
    
    参数：
    - url: 图片 URL
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': '请提供图片 URL'}), 400
        
        # 验证 URL 格式
        if not url.startswith(('http://', 'https://')):
            return jsonify({'error': 'URL 必须以 http:// 或 https:// 开头'}), 400
        
        # 注意：你的 URL 有 ?imageMogr2/format/jpeg 参数，这会把 PNG 转成 JPEG
        # 需要移除这个参数或改成 format/png
        if '?imageMogr2/format/jpeg' in url:
            # 移除或替换为 PNG
            url = url.split('?')[0]  # 直接移除参数获取原图
        
        # 获取图片
        import urllib.request
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=30) as response:
            image_data = response.read()
            content_type = response.headers.get('Content-Type', 'image/png')
        
        # 返回图片
        return send_file(
            io.BytesIO(image_data),
            mimetype=content_type,
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': f'获取图片失败: {str(e)}'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=False)
