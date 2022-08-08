import csv
import jieba
import numpy
from PIL import Image
from wordcloud import WordCloud

# 获取评论字符串
comments = ''
with open('data/douban.csv', 'r', encoding='utf-8') as fr:
    reader = csv.reader(fr)
    for line in reader:
        comments += line[1]
result = jieba.cut(comments)
result = list(result)
text = ' '.join(result)
image = numpy.array(Image.open('pictures/sheep.jpg'))
wcloud = WordCloud(font_path='simsun.ttc', mask=image)
wcloud.generate(text)
wcloud.to_file('pictures/result_picture.png')