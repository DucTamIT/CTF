import re
import time
import os
from pathlib import Path


flag = os.environ.get('GZCTF_FLAG')

if not flag:
    FLAG_PATH = Path(os.environ.get('FLAG_PATH', '/flag.txt'))
    flag = FLAG_PATH.read_text(encoding='utf-8').strip()


secret_intro = \
'''Từng byte lang thang giữa miền ký ức,
Một vùng bí mật vẫn chưa ai đánh thức.
Khi con trỏ quay về nơi bắt đầu,
Bộ nhớ chỉ còn giữ lại tên nhau: '''\
+ flag + '\n'


# Song title: Tràn Bộ Nhớ
song_tran_bo_nho = secret_intro +\
'''

[REFRAIN]
Dữ liệu cứ tràn qua miền ký ức,
Ghi đè lên những giới hạn ngày xưa.
Con trỏ lạc giữa muôn vùng địa chỉ,
Chỉ một lần quay lại cũng thành dư thừa.
CROWD (Hát cùng nào!);
RETURN

[VERSE1]
Đêm nay màn hình xanh màu rất lạ,
Từng dòng lệnh chạy mãi chẳng chịu ngừng.
Anh gom nỗi nhớ vào trong một mảng,
Nhưng kích thước nào chứa hết mông lung?
Một ký tự rơi ngoài miền cho phép,
Cả chương trình bỗng đứng lại giữa chừng.

REFRAIN;

Stack vẫn lặng im chờ ai gọi đến,
Thanh ghi mang theo địa chỉ quay về.
Anh viết tên em dài hơn giới hạn,
Để lối cũ không còn biết đường về.
Giữa những byte không tên nằm nối tiếp,
Một bí mật ngủ quên dưới bộ nhớ mê.

REFRAIN;

Debugger dừng ngay nơi lời chưa nói,
Breakpoint sáng lên giữa một đêm dài.
Từng opcode kể câu chuyện dang dở,
Rằng lỗi nhỏ kia đâu phải tình cờ.
Theo con trỏ qua từng vùng địa chỉ,
Anh tìm ra điều được giấu trong mơ.

REFRAIN;

Canary đứng canh bên miền ký ức,
NX khép đường và ASLR giăng sương.
Nhưng những gadget rời rạc khi ghép lại,
Vẫn mở ra thêm một lối lên đường.
Mỗi địa chỉ là một lời nhắn gửi,
Nối thành chuỗi gọi bình minh thức dậy.

REFRAIN;

Payload trôi qua khung vùng chật hẹp,
Padding lấp đầy khoảng trống phía sau.
Base pointer thôi không còn nguyên vẹn,
Return address đổi hướng tự khi nào.
Một shell nhỏ vang lên trong im lặng,
Mở cánh cửa từng khóa kín rất lâu.

REFRAIN;

Nếu bộ nhớ có một ngày đầy quá,
Hãy để dòng này ghi tiếp tên em.
Qua giới hạn mà người ta đã đặt,
Qua cả vùng an toàn giữa bóng đêm.
Khi chương trình quay về nơi khởi điểm,
Flag thức dậy và hiện sáng bên thềm.

REFRAIN;

END;
'''

MAX_LINES = 100


def reader(song, startLabel):
    lip = 0
    start = 0
    refrain = 0
    refrain_return = 0
    finished = False

    # Get list of lyric lines
    song_lines = song.splitlines()

    # Find startLabel, refrain and refrain return
    for i in range(0, len(song_lines)):
        if song_lines[i] == startLabel:
            start = i + 1
        elif song_lines[i] == '[REFRAIN]':
            refrain = i + 1
        elif song_lines[i] == 'RETURN':
            refrain_return = i

    # Print lyrics
    line_count = 0
    lip = start
    while not finished and line_count < MAX_LINES:
        line_count += 1
        for line in song_lines[lip].split(';'):
            if line == '' and song_lines[lip] != '':
                continue
            if line == 'REFRAIN':
                song_lines[refrain_return] = 'RETURN ' + str(lip + 1)
                lip = refrain
            elif re.match(r"CROWD.*", line):
                crowd = input('Crowd: ')
                song_lines[lip] = 'Crowd: ' + crowd
                lip += 1
            elif re.match(r"RETURN [0-9]+", line):
                lip = int(line.split()[1])
            elif line == 'END':
                finished = True
            else:
                print(line, flush=True)
                time.sleep(0.5)
                lip += 1


reader(song_tran_bo_nho, '[VERSE1]')
