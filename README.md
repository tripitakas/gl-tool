# 高丽藏数据整理工具
韩国高丽藏研究所于2004年发布高丽藏数字化成果光盘，包括word版本的原字文本（Doc文件夹）、text版本的unicode文本（Text文件夹）等以及支持全文检索的软件工具和异体字字典。
本项目旨在对这些数字化内容进行检查和完善，以服务于如是古籍数字化工程。

# 准备工作
- 统计unicode文本中的文字种类及字频，并进行分析
 * 针对其中的所有字种，检查是否为unicode，以及字形是否与unicode字形一致
 * 如果不是unicode，则查找unicode13.0版本的字符集进行补充
详见《高丽藏异体字字典缺失的字头.xlsx》

# c#
## 1. 从Docx文件夹提取原字文本并按页拆分，结果存放至DocxOriTxt0文件夹

## 2. 从Text文件夹按页拆分，结果存放至Text2Page0文件夹

# python
## 3. 去掉DocxOriTxt0中的噪音，结果存放至DocxOriTxt文件夹

## 4. 根据异体字字典，将DocxOriTxt中的原字文本转换为正字文本，结果存放至DocxStdTxt文件夹

## 5. 将Text2Page0与DocxStdTxt中的文件进行比较，互相校验和完善，使得每份文本的总行数以及每行字数均相同


## 整理结果
1. DocxOriTxt原字文本
2. DocxStdTxt正字文本
3. Text2Page通字文本

详见链接: https://pan.baidu.com/s/1uCuILHblaR-Y70IV6IF58g(提取码: lrw5)
