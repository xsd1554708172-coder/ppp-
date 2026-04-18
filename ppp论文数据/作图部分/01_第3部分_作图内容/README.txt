PPP 第3部分 6张主图复现包

用途
- 复现以下 6 张图：
  Figure_3_1_code_coverage_strength
  Figure_3_3_code_cooccurrence_network
  Figure_3_4_dictionary_workflow
  Figure_3_8_expansion_screening_funnel
  Figure_3_9_topic_dynamics_panels
  Figure_3_14_labelwise_dumbbell_grid

目录结构
- input_data/: 代码运行所需的 5 个 Excel 输入文件（已整理好）
- charts/: 当前生成好的图（PNG + PDF）
- generate_part3_main6_redo_repro.py: 可直接运行的复现脚本
- requirements.txt: 最小依赖

如何运行
1. 安装依赖：pip install -r requirements.txt
2. 进入本目录，运行：python generate_part3_main6_redo_repro.py
3. 新生成的图会输出到 charts_regenerated/

注意
- 脚本使用相对路径，不依赖 /mnt/data 这类容器路径。
- 若本机没有 Noto Sans CJK SC，会自动尝试 Microsoft YaHei / SimHei / Arial Unicode MS / DejaVu Sans。
- 输入数据文件名已统一成英文，避免压缩包解压乱码。