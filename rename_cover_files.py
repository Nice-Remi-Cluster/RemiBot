#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面文件重命名脚本
将大于10000的文件名对10000取余处理
"""

import os
import shutil
from pathlib import Path
from loguru import logger

def rename_cover_files():
    """
    重命名封面文件，将大于10000的ID对10000取余
    """
    cover_dir = Path("resources/yuzu/static/mai/cover")
    
    if not cover_dir.exists():
        logger.error(f"封面目录不存在: {cover_dir}")
        return
    
    logger.info(f"开始处理封面文件: {cover_dir}")
    
    # 获取所有png文件
    png_files = list(cover_dir.glob("*.png"))
    logger.info(f"找到 {len(png_files)} 个封面文件")
    
    # 统计信息
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    # 创建备份目录
    backup_dir = cover_dir.parent / "cover_backup"
    backup_dir.mkdir(exist_ok=True)
    logger.info(f"备份目录: {backup_dir}")
    
    for png_file in png_files:
        try:
            # 获取文件名（不含扩展名）
            file_stem = png_file.stem
            
            # 尝试转换为整数
            try:
                file_id = int(file_stem)
            except ValueError:
                logger.warning(f"跳过非数字文件名: {png_file.name}")
                skipped_count += 1
                continue
            
            # 如果ID大于等于10000，进行取余处理
            if file_id >= 10000:
                new_id = file_id % 10000
                new_filename = f"{new_id}.png"
                new_path = cover_dir / new_filename
                
                # 备份原文件
                backup_path = backup_dir / png_file.name
                shutil.copy2(png_file, backup_path)
                
                # 检查目标文件是否已存在
                if new_path.exists():
                    logger.warning(f"目标文件已存在，跳过重命名: {file_id} -> {new_id} ({png_file.name})")
                    skipped_count += 1
                    continue
                
                # 重命名文件
                png_file.rename(new_path)
                logger.info(f"重命名: {file_id} -> {new_id} ({png_file.name} -> {new_filename})")
                renamed_count += 1
            else:
                # ID小于10000，不需要处理
                skipped_count += 1
                
        except Exception as e:
            logger.error(f"处理文件 {png_file.name} 时出错: {e}")
            error_count += 1
    
    # 输出统计信息
    logger.info("处理完成！")
    logger.info(f"重命名文件数: {renamed_count}")
    logger.info(f"跳过文件数: {skipped_count}")
    logger.info(f"错误文件数: {error_count}")
    logger.info(f"备份目录: {backup_dir}")

def preview_rename_operations():
    """
    预览重命名操作，不实际执行
    """
    cover_dir = Path("resources/yuzu/static/mai/cover")
    
    if not cover_dir.exists():
        logger.error(f"封面目录不存在: {cover_dir}")
        return
    
    logger.info(f"预览重命名操作: {cover_dir}")
    
    # 获取所有png文件
    png_files = list(cover_dir.glob("*.png"))
    logger.info(f"找到 {len(png_files)} 个封面文件")
    
    # 统计信息
    will_rename = []
    will_skip = []
    conflicts = []
    
    for png_file in png_files:
        try:
            # 获取文件名（不含扩展名）
            file_stem = png_file.stem
            
            # 尝试转换为整数
            try:
                file_id = int(file_stem)
            except ValueError:
                will_skip.append((png_file.name, "非数字文件名"))
                continue
            
            # 如果ID大于等于10000，进行取余处理
            if file_id >= 10000:
                new_id = file_id % 10000
                new_filename = f"{new_id}.png"
                new_path = cover_dir / new_filename
                
                # 检查目标文件是否已存在
                if new_path.exists():
                    conflicts.append((png_file.name, new_filename, "目标文件已存在"))
                else:
                    will_rename.append((png_file.name, new_filename, f"{file_id} -> {new_id}"))
            else:
                will_skip.append((png_file.name, "ID小于10000"))
                
        except Exception as e:
            will_skip.append((png_file.name, f"处理错误: {e}"))
    
    # 输出预览结果
    print("\n=== 重命名预览 ===")
    print(f"将要重命名的文件 ({len(will_rename)} 个):")
    for old_name, new_name, reason in will_rename[:20]:  # 只显示前20个
        print(f"  {old_name} -> {new_name} ({reason})")
    if len(will_rename) > 20:
        print(f"  ... 还有 {len(will_rename) - 20} 个文件")
    
    print(f"\n将要跳过的文件 ({len(will_skip)} 个):")
    for file_name, reason in will_skip[:10]:  # 只显示前10个
        print(f"  {file_name} ({reason})")
    if len(will_skip) > 10:
        print(f"  ... 还有 {len(will_skip) - 10} 个文件")
    
    if conflicts:
        print(f"\n冲突文件 ({len(conflicts)} 个):")
        for old_name, new_name, reason in conflicts:
            print(f"  {old_name} -> {new_name} ({reason})")
    
    print(f"\n总计: {len(png_files)} 个文件")
    print(f"  - 将重命名: {len(will_rename)} 个")
    print(f"  - 将跳过: {len(will_skip)} 个")
    print(f"  - 冲突: {len(conflicts)} 个")

def main():
    """
    主函数
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        print("预览模式 - 不会实际修改文件")
        preview_rename_operations()
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("执行模式 - 将实际重命名文件")
        confirm = input("确认要执行重命名操作吗？(y/N): ")
        if confirm.lower() in ['y', 'yes']:
            rename_cover_files()
        else:
            print("操作已取消")
    else:
        print("封面文件重命名脚本")
        print("用法:")
        print("  python rename_cover_files.py --preview   # 预览重命名操作")
        print("  python rename_cover_files.py --execute   # 执行重命名操作")
        print("")
        print("说明:")
        print("  - 将大于等于10000的文件ID对10000取余")
        print("  - 执行前会自动创建备份")
        print("  - 如果目标文件已存在，将跳过重命名")

if __name__ == "__main__":
    main()