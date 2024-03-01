# AD_Intelligent_Diagnosis

✨ **基于 深度学习 和 ADNI 数据集的阿尔兹海默智能诊断 Web 应用**


## 功能简介

- 1, 根据脑部 MRI 医学影像智能诊断阿尔兹海默病
- 2, 绘制参数相关性热力图
- 3, 使用纯 python 编写，轻量化，易复现，易部署
- 4, 代码可读性高

## 如何使用

python 版本 3.7

需要 `16GB` 以上内存

安装依赖

```bash
pip install -r requirement.txt
```

zlzheimer-diagnostic-system.py 是项目入口，运行此文件即可启动服务器

```bash
python zlzheimer-diagnostic-system.py
```

## 项目结构

```
└─AD_Intelligent_Diagnosis
    ├─demodata
    ├─model_save
    ├─uploaded_img
    ├─readme_static
    │  ├─AD
    │  ├─CN
    │  ├─EMCI
    │  ├─LMCI
    │  └─MCI
    └─run_logs
```

- demodata 文件夹存放示例图片
- model_save 文件夹存放存放训练好的模型
- uploaded_img 文件夹存放用户上传的医学影像
- readme_static 文件夹内存放了一些五个类别的影像文件用于测试
- run_logs 存放用户访问日志

