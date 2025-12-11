# 商品图片上传辅助脚本
import os
import shutil
from datetime import datetime

def create_image_directories():
    """创建图片存储目录"""
    base_dir = "static/img/goods"

    # 创建目录结构
    os.makedirs(base_dir, exist_ok=True)
    print(f"✅ 创建目录: {os.path.abspath(base_dir)}")

    return os.path.abspath(base_dir)

def list_image_files(directory):
    """列出目录中的图片文件"""
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    image_files = []

    if os.path.exists(directory):
        for file in os.listdir(directory):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(file)

    return image_files

def upload_images(source_dir=None):
    """
    上传图片到项目目录

    Args:
        source_dir: 图片源目录，如果为None，则需要手动复制
    """
    # 创建目标目录
    target_dir = create_image_directories()

    if source_dir and os.path.exists(source_dir):
        # 从指定目录复制图片
        image_files = list_image_files(source_dir)
        copied_count = 0

        for file in image_files:
            source_path = os.path.join(source_dir, file)
            target_path = os.path.join(target_dir, file)

            # 复制文件
            shutil.copy2(source_path, target_path)
            copied_count += 1
            print(f"✓ 复制: {file}")

        print(f"\n成功复制 {copied_count} 张图片到项目目录")

    else:
        print("\n请手动将图片复制到以下目录:")
        print(f"📁 {target_dir}")
        print("\n提示:")
        print("- 支持 PNG、JPG、JPEG、GIF、BMP 格式")
        print("- 建议图片尺寸: 300x300 像素或以上")
        print("- 建议文件大小: 小于 2MB")

def generate_image_urls():
    """生成商品图片URL列表"""
    target_dir = "static/img/goods"
    image_files = list_image_files(target_dir)

    urls = []
    for file in image_files:
        url = f"/static/img/goods/{file}"
        urls.append({
            'filename': file,
            'url': url,
            'size': f"{os.path.getsize(os.path.join(target_dir, file)) / 1024:.2f} KB"
        })

    return urls

if __name__ == "__main__":
    print("=== 商品图片上传工具 ===\n")

    # 选择操作
    print("1. 创建图片目录")
    print("2. 从指定目录复制图片")
    print("3. 查看已上传的图片")
    print("4. 生成图片URL列表")

    choice = input("\n请选择操作 (1-4): ")

    if choice == "1":
        create_image_directories()
    elif choice == "2":
        source = input("请输入图片源目录路径: ")
        upload_images(source if source else None)
    elif choice == "3":
        urls = generate_image_urls()
        if urls:
            print("\n已上传的图片:")
            for item in urls:
                print(f"- {item['filename']} ({item['size']})")
                print(f"  URL: {item['url']}")
        else:
            print("\n暂无图片")
    elif choice == "4":
        urls = generate_image_urls()
        if urls:
            print("\n图片URL列表:")
            for item in urls:
                print(f"{item['url']}")
        else:
            print("\n暂无图片")
    else:
        # 默认创建目录
        upload_images()