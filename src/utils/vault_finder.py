"""
옵시디언 볼트 경로를 찾는 유틸리티
"""
import os
from pathlib import Path

def find_obsidian_vaults():
    """
    일반적인 옵시디언 볼트 위치들을 검색
    """
    possible_locations = [
        # macOS
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Library/Application Support/obsidian"),
        os.path.expanduser("~/Obsidian"),
        # 현재 디렉토리와 그 상위 디렉토리들도 검색
        os.getcwd(),
        str(Path(os.getcwd()).parent),
    ]
    
    vaults = []
    
    for location in possible_locations:
        if not os.path.exists(location):
            continue
            
        # .obsidian 폴더가 있는 디렉토리를 찾음
        for root, dirs, files in os.walk(location):
            if '.obsidian' in dirs:
                vaults.append(root)
                
            # 너무 깊이 들어가지 않도록 제한
            if root.count(os.sep) - location.count(os.sep) > 3:
                dirs.clear()
    
    return vaults

def is_valid_vault(path):
    """
    주어진 경로가 유효한 옵시디언 볼트인지 확인
    """
    obsidian_dir = os.path.join(path, '.obsidian')
    return os.path.isdir(obsidian_dir)

if __name__ == "__main__":
    print("옵시디언 볼트 검색 중...")
    vaults = find_obsidian_vaults()
    
    if vaults:
        print("\n발견된 옵시디언 볼트:")
        for i, vault in enumerate(vaults, 1):
            print(f"{i}. {vault}")
    else:
        print("옵시디언 볼트를 찾을 수 없습니다.")
