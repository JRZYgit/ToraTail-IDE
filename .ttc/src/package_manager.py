import os
import json
import sys
import shutil
from pathlib import Path
import hashlib
from datetime import datetime

class PackageManager:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.tora_packages_dir = self.project_root / "tora_packages"
        self.package_config_file = self.project_root / "tora.json"
        self.packages_cache_dir = self.tora_packages_dir / ".cache"
        self.registry_url = "https://tora-packages.registry.com"  # 模拟包注册表URL
        
    def init_project(self, name=None, version="0.1.0", description="", author=""):
        """初始化一个新的Tora项目"""
        # 创建项目目录结构
        self.tora_packages_dir.mkdir(exist_ok=True)
        self.packages_cache_dir.mkdir(exist_ok=True)
        
        # 创建默认的包配置文件
        if not name:
            name = self.project_root.name
            
        package_config = {
            "name": name,
            "version": version,
            "description": description,
            "author": author,
            "dependencies": {},
            "devDependencies": {}
        }
        
        with open(self.package_config_file, 'w', encoding='utf-8') as f:
            json.dump(package_config, f, indent=2, ensure_ascii=False)
            
        print(f"Initialized new Tora project: {name}")
        return package_config
    
    def load_package_config(self):
        """加载包配置文件"""
        if not self.package_config_file.exists():
            raise FileNotFoundError("tora.json not found. Run 'tora init' first.")
            
        with open(self.package_config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_package_config(self, config):
        """保存包配置文件"""
        with open(self.package_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def install_package(self, package_name, version=None, dev=False):
        """安装包"""
        try:
            config = self.load_package_config()
        except FileNotFoundError:
            print("Error: This directory is not a Tora project. Run 'tora init' first.")
            return
            
        # 检查包是否已安装
        dep_type = "devDependencies" if dev else "dependencies"
        if package_name in config[dep_type]:
            if version is None or config[dep_type][package_name] == version:
                print(f"Package '{package_name}' is already installed.")
                return
        
        # 尝试从缓存安装
        if self._install_from_cache(package_name, version):
            print(f"Installed {package_name} from cache")
        else:
            # 从远程仓库下载包
            print(f"Installing package: {package_name}" + (f"@{version}" if version else ""))
            
            # 创建包目录
            package_dir = self.tora_packages_dir / package_name
            package_dir.mkdir(exist_ok=True)
            
            # 下载包文件
            if self._download_package(package_name, version, package_dir):
                # 更新依赖配置
                config[dep_type][package_name] = version or "latest"
                self.save_package_config(config)
                
                print(f"Successfully installed package: {package_name}")
            else:
                print(f"Failed to install package: {package_name}")
    
    def _install_from_cache(self, package_name, version):
        """从缓存安装包"""
        cache_package_dir = self.packages_cache_dir / package_name
        if cache_package_dir.exists():
            # 复制缓存到项目目录
            target_dir = self.tora_packages_dir / package_name
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(cache_package_dir, target_dir)
            return True
        return False
    
    def _download_package(self, package_name, version, package_dir):
        """下载包（模拟实现）"""
        try:
            # 在实际实现中，这里会从远程仓库下载包
            # 创建模拟的包文件
            self._create_mock_package(package_dir, package_name, version)
            
            # 保存到缓存
            cache_package_dir = self.packages_cache_dir / package_name
            if cache_package_dir.exists():
                shutil.rmtree(cache_package_dir)
            shutil.copytree(package_dir, cache_package_dir)
            
            return True
        except Exception as e:
            print(f"Error downloading package: {e}")
            return False
    
    def _create_mock_package(self, package_dir, package_name, version):
        """创建模拟包文件（用于演示）"""
        # 创建主模块文件
        main_file = package_dir / f"{package_name}.tora"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(f'// {package_name} package\n')
            f.write(f'// Version: {version or "1.0.0"}\n\n')
            f.write(f'fn {package_name}_hello() {{\n')
            f.write(f'    println("Hello from {package_name} package!");\n')
            f.write('}\n\n')
            f.write(f'fn {package_name}_version() {{\n')
            f.write(f'    println("Version: {version or "1.0.0"}");\n')
            f.write('}\n')
        
        # 创建包信息文件
        package_info = {
            "name": package_name,
            "version": version or "1.0.0",
            "description": f"A sample {package_name} package for Tora",
            "author": "Tora Package Team",
            "license": "MIT",
            "files": [f"{package_name}.tora"],
            "dependencies": {},
            "createdAt": datetime.now().isoformat()
        }
        
        with open(package_dir / "package.json", 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2)
    
    def uninstall_package(self, package_name):
        """卸载包"""
        try:
            config = self.load_package_config()
        except FileNotFoundError:
            print("Error: This directory is not a Tora project. Run 'tora init' first.")
            return
            
        # 检查包是否在依赖中
        removed = False
        for dep_type in ["dependencies", "devDependencies"]:
            if package_name in config[dep_type]:
                del config[dep_type][package_name]
                removed = True
        
        if not removed:
            print(f"Package '{package_name}' is not installed.")
            return
            
        # 删除包目录
        package_dir = self.tora_packages_dir / package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)
            print(f"Removed package directory: {package_dir}")
        
        # 更新依赖配置
        self.save_package_config(config)
        
        print(f"Successfully uninstalled package: {package_name}")
    
    def list_packages(self, all_deps=False):
        """列出已安装的包"""
        try:
            config = self.load_package_config()
        except FileNotFoundError:
            print("Error: This directory is not a Tora project. Run 'tora init' first.")
            return
            
        dependencies = config.get("dependencies", {})
        dev_dependencies = config.get("devDependencies", {})
        
        if not dependencies and not dev_dependencies:
            print("No packages installed.")
            return
            
        print("Installed packages:")
        if dependencies:
            print("  Dependencies:")
            for package_name, version in dependencies.items():
                print(f"    {package_name}@{version}")
        
        if all_deps and dev_dependencies:
            print("  Dev Dependencies:")
            for package_name, version in dev_dependencies.items():
                print(f"    {package_name}@{version}")
    
    def update_package(self, package_name):
        """更新包"""
        print(f"Updating package: {package_name}")
        # 在实际实现中，这里会检查远程仓库的最新版本并更新
        print(f"Package '{package_name}' updated to latest version.")
    
    def update_all_packages(self):
        """更新所有包"""
        try:
            config = self.load_package_config()
        except FileNotFoundError:
            print("Error: This directory is not a Tora project. Run 'tora init' first.")
            return
            
        dependencies = config.get("dependencies", {})
        dev_dependencies = config.get("devDependencies", {})
        all_packages = {**dependencies, **dev_dependencies}
        
        if not all_packages:
            print("No packages to update.")
            return
            
        print("Updating all packages...")
        for package_name in all_packages:
            self.update_package(package_name)
        print("All packages updated.")
    
    def search_packages(self, query):
        """搜索包（模拟实现）"""
        # 在实际实现中，这里会查询远程包仓库
        print(f"Searching for packages matching: {query}")
        print("Found packages:")
        print(f"  {query}-utils - Utility functions for {query}")
        print(f"  {query}-lib - Library for {query} operations")
        print(f"  {query}-tools - Tools for {query} development")
        print(f"  {query}-core - Core functionality for {query}")
    
    def publish_package(self):
        """发布包到注册表"""
        try:
            config = self.load_package_config()
        except FileNotFoundError:
            print("Error: This directory is not a Tora project. Run 'tora init' first.")
            return
            
        package_name = config.get("name")
        version = config.get("version")
        
        print(f"Publishing package: {package_name}@{version}")
        # 在实际实现中，这里会将包上传到远程注册表
        print("Package published successfully!")
    
    def info_package(self, package_name):
        """显示包信息"""
        package_dir = self.tora_packages_dir / package_name
        package_info_file = package_dir / "package.json"
        
        if not package_info_file.exists():
            print(f"Package '{package_name}' not found.")
            return
            
        with open(package_info_file, 'r', encoding='utf-8') as f:
            package_info = json.load(f)
            
        print(f"Package: {package_info.get('name')}")
        print(f"Version: {package_info.get('version')}")
        print(f"Description: {package_info.get('description')}")
        print(f"Author: {package_info.get('author')}")
        print(f"License: {package_info.get('license')}")
        print(f"Created: {package_info.get('createdAt')}")
    
    def clean_cache(self):
        """清理包缓存"""
        if self.packages_cache_dir.exists():
            shutil.rmtree(self.packages_cache_dir)
            self.packages_cache_dir.mkdir(exist_ok=True)
            print("Package cache cleaned.")
        else:
            print("No cache to clean.")
    
    def show_project_info(self):
        """显示项目信息"""
        try:
            config = self.load_package_config()
        except FileNotFoundError:
            print("Error: This directory is not a Tora project. Run 'tora init' first.")
            return
            
        print("Project Information:")
        print(f"  Name: {config.get('name')}")
        print(f"  Version: {config.get('version')}")
        print(f"  Description: {config.get('description')}")
        print(f"  Author: {config.get('author')}")
        
        dependencies = config.get("dependencies", {})
        dev_dependencies = config.get("devDependencies", {})
        
        if dependencies:
            print("  Dependencies:")
            for package_name, version in dependencies.items():
                print(f"    {package_name}@{version}")
        
        if dev_dependencies:
            print("  Dev Dependencies:")
            for package_name, version in dev_dependencies.items():
                print(f"    {package_name}@{version}")

def main():
    """包管理器命令行接口"""
    if len(sys.argv) < 2:
        print("Tora Package Manager")
        print("Usage: tora [command] [options]")
        print("\nCommands:")
        print("  init [name]              Initialize a new Tora project")
        print("  install <package>        Install a package")
        print("  install-dev <package>    Install a development package")
        print("  uninstall <package>      Uninstall a package")
        print("  list                     List installed packages")
        print("  list-all                 List all packages (including dev)")
        print("  update <package>         Update a package")
        print("  update-all               Update all packages")
        print("  search <query>           Search for packages")
        print("  info <package>           Show package information")
        print("  publish                  Publish current package")
        print("  clean-cache              Clean package cache")
        print("  project-info             Show project information")
        return
    
    command = sys.argv[1]
    pm = PackageManager()
    
    if command == "init":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        # 获取额外参数
        version = "0.1.0"
        description = ""
        author = ""
        for i in range(3, len(sys.argv)):
            if sys.argv[i].startswith("--version="):
                version = sys.argv[i].split("=", 1)[1]
            elif sys.argv[i].startswith("--description="):
                description = sys.argv[i].split("=", 1)[1]
            elif sys.argv[i].startswith("--author="):
                author = sys.argv[i].split("=", 1)[1]
        pm.init_project(name, version, description, author)
    elif command == "install":
        if len(sys.argv) < 3:
            print("Usage: tora install <package>[@version]")
            return
        package_spec = sys.argv[2]
        if "@" in package_spec:
            package_name, version = package_spec.split("@", 1)
            pm.install_package(package_name, version)
        else:
            pm.install_package(package_spec)
    elif command == "install-dev":
        if len(sys.argv) < 3:
            print("Usage: tora install-dev <package>[@version]")
            return
        package_spec = sys.argv[2]
        if "@" in package_spec:
            package_name, version = package_spec.split("@", 1)
            pm.install_package(package_name, version, dev=True)
        else:
            pm.install_package(package_spec, dev=True)
    elif command == "uninstall":
        if len(sys.argv) < 3:
            print("Usage: tora uninstall <package>")
            return
        pm.uninstall_package(sys.argv[2])
    elif command == "list":
        pm.list_packages()
    elif command == "list-all":
        pm.list_packages(all_deps=True)
    elif command == "update":
        if len(sys.argv) < 3:
            print("Usage: tora update <package>")
            return
        pm.update_package(sys.argv[2])
    elif command == "update-all":
        pm.update_all_packages()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: tora search <query>")
            return
        pm.search_packages(sys.argv[2])
    elif command == "info":
        if len(sys.argv) < 3:
            print("Usage: tora info <package>")
            return
        pm.info_package(sys.argv[2])
    elif command == "publish":
        pm.publish_package()
    elif command == "clean-cache":
        pm.clean_cache()
    elif command == "project-info":
        pm.show_project_info()
    else:
        print(f"Unknown command: {command}")
        print("Run 'tora' without arguments for help.")

if __name__ == "__main__":
    main()