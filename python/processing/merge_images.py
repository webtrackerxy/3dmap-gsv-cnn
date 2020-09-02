import os

file = 'out.jpg'
crop_file = 'crop_file.jpg'

cmd = 'montage 6obys-cnZOkqmmeRuTCTFg_0_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_1_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_2_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_3_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_4_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_5_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_6_0_3.jpg 6obys-cnZOkqmmeRuTCTFg_0_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_1_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_2_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_3_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_4_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_5_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_6_1_3.jpg 6obys-cnZOkqmmeRuTCTFg_0_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_1_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_2_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_3_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_4_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_5_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_6_2_3.jpg 6obys-cnZOkqmmeRuTCTFg_0_3_3.jpg 6obys-cnZOkqmmeRuTCTFg_1_3_3.jpg 6obys-cnZOkqmmeRuTCTFg_2_3_3.jpg 6obys-cnZOkqmmeRuTCTFg_3_3_3.jpg 6obys-cnZOkqmmeRuTCTFg_4_3_3.jpg 6obys-cnZOkqmmeRuTCTFg_5_3_3.jpg 6obys-cnZOkqmmeRuTCTFg_6_3_3.jpg -mode Concatenate -tile 7x4 out.jpg'
print(cmd)
os.system(cmd)
cmd = 'convert "' + file+'" -crop 3328x1664+0+0 "'+ crop_file + '"'
print(cmd)
os.system(cmd)
