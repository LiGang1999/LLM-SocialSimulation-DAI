import os
import shutil
import json
import re


def copy_directory_structure(src_dir, dst_dir, exclude_file=None):
    """复制目录结构，但排除特定文件"""
    for root, dirs, files in os.walk(src_dir):
        # 计算相对路径
        relative_path = os.path.relpath(root, src_dir)
        dst_root = os.path.join(dst_dir, relative_path)

        # 创建目录
        os.makedirs(dst_root, exist_ok=True)

        # 复制文件
        for file in files:
            if file != exclude_file:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_root, file)
                shutil.copy2(src_file, dst_file)


def organize_profiles():
    # 基础配置
    source_dirs = ["generated_profiles"]
    target_base_dir = "shbz2"
    template_dir = "personas/林敏"  # 使用林敏的目录结构作为模板

    # 创建主目录
    if not os.path.exists(target_base_dir):
        os.makedirs(target_base_dir)

    # 遍历所有源目录
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            continue

        # 处理每个JSON文件
        for filename in os.listdir(source_dir):
            if not filename.endswith(".json"):
                continue

            # 提取用户编号
            match = re.search(r"用户(\d+)", filename)
            if not match:
                continue

            user_num = match.group(1)
            user_dir = os.path.join(target_base_dir, f"用户{user_num}")

            # 复制整个目录结构（除了scratch.json）
            copy_directory_structure(template_dir, user_dir, "scratch.json")

            # 复制并重命名用户配置文件
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(user_dir, "bootstrap_memory", "scratch.json")

            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # 复制文件
            shutil.copy2(source_path, target_path)

            print(f"已处理用户{user_num}的配置文件")


if __name__ == "__main__":
    organize_profiles()
