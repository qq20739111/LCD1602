# ########################################
# LCD1602 MicroPython 直连控制库
# 示例程序：主要功能测试程序
# 四个高位数据引脚依次连接到MCU的4、5、6、7引脚

import time
from LCD1602 import LCD1602

# 创建 LCD1602 实例
lcd = LCD1602()
# 设置数据传输模式4bits，采用4根数据线连接
lcd.set_data_trans_bits(4)
# 设置LCD引脚对应连接的GPIO
lcd.enable_pin("V0", 0)
lcd.enable_pin("RS", 1)
lcd.enable_pin("RW", 2)
lcd.enable_pin("E", 3)
lcd.enable_pin("D4", 4) # 数据传输模式为4bits 需要采用高4位引脚
lcd.enable_pin("D5", 5)
lcd.enable_pin("D6", 6)
lcd.enable_pin("D7", 7)
# 根据设置 初始化 LCD1602
lcd.init()
# 通过终端打印所有引脚状态信息
lcd.terminal_print_pins()
# 通过PWM设置对比度为40%
lcd.display_contrast(40)

# 向屏幕写入数据
lcd.print_line("Hello, World", 0)
time.sleep(1)  # 等待1秒

# 清屏
lcd.clear()
time.sleep(1)  # 等待1秒
# 打印单个字符
lcd.print_char("A") # 打印到当前光标处
time.sleep(1)  # 等待1秒
lcd.print_char("B") # 打印到当前光标处
time.sleep(1)  # 等待1秒
lcd.print_char("C") # 打印到当前光标处
time.sleep(1)  # 等待1秒
# 按指定行打印
lcd.print_line("Test PrintLine0", 0) # 打印到第1行
time.sleep(1)  # 等待1秒
lcd.print_line("Test PrintLine1", 1) # 打印到第2行
time.sleep(1)  # 等待1秒
lcd.clear_line(0) # 清除第1行
time.sleep(1)  # 等待1秒
lcd.clear_line(1) # 清除第2行
time.sleep(1)  # 等待1秒
# 翻页打印长文本
long_text = """This MicroPython LCD1602 module provides a comprehensive interface for controlling 16x2 character LCDs. It supports both 4-bit and 8-bit data modes, flexible pin mapping, and advanced features such as contrast and backlight control via PWM. The module includes high-level methods for printing text, clearing lines, cursor movement, and display effects like scrolling and blinking.
A highlight of the module is the Browser feature, which allows you to manage and display large amounts of text on the limited LCD screen. The Browser automatically splits long text into lines, supports line-by-line or page-by-page scrolling, and lets you control the scroll speed and display any line or range with ease. This makes it ideal for applications that need to present logs, menus, or long messages on a small LCD."""
lcd.print(long_text, 2) # 打印速度2页/秒
# 横向滚动显示
text1 = "Scroll test!"
text2 = """! "#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~°¢¥→←↑↓■"""
lcd.scroll_line(text1, 0, speed=3)
lcd.scroll_line(text2, 1, speed=7)
time.sleep(1)  # 等待1秒

# 屏幕光标控制
lcd.print_line("Cursor Show,Move", 0)
time.sleep(1)  # 等待1秒
lcd.display_off() # 关闭显示
time.sleep(1)  # 等待1秒
lcd.cursor_position(1, 8) # 移动光标到第2行第9列
lcd.display_on() # 开启显示
time.sleep(1)  # 等待1秒
lcd.hide_blink_cursor() # 隐藏闪烁和光标
time.sleep(1)  # 等待1秒
lcd.show_cursor() # 显示静态光标
time.sleep(1)  # 等待1秒
lcd.cursor_move_left()
time.sleep(1)  # 等待1秒
lcd.show_blink() # 显示闪烁
time.sleep(1)  # 等待1秒
lcd.cursor_move_left()
time.sleep(1)  # 等待1秒
lcd.show_blink_cursor() # 显示闪烁光标
time.sleep(1)  # 等待1秒

# 光标移动
lcd.cursor_home() # 光标归位
time.sleep(1)  # 等待1秒
lcd.cursor_move_down() # 光标下移
time.sleep(1)  # 等待1秒
lcd.print_char("A")
time.sleep(1)  # 等待1秒
lcd.cursor_move_right()  # 光标右移
time.sleep(1)  # 等待1秒
lcd.print_char("B")
time.sleep(1)  # 等待1秒
lcd.cursor_move_left()  # 光标左移
time.sleep(1)  # 等待1秒
lcd.print_char("C")
time.sleep(1)  # 等待1秒
lcd.print_char("D")
time.sleep(1)  # 等待1秒
lcd.print_char("E")
time.sleep(1)  # 等待1秒
lcd.cursor_move_up()  # 光标上移
time.sleep(1)  # 等待1秒
lcd.cursor_move_right()
time.sleep(1)  # 等待1秒
lcd.cursor_move_right()
time.sleep(1)  # 等待1秒
lcd.print_char("H")
time.sleep(1)  # 等待1秒
lcd.print_char("i")
time.sleep(1)  # 等待1秒
lcd.print_char("d")
time.sleep(1)  # 等待1秒
lcd.print_char("e")
time.sleep(1)  # 等待1秒

# 长文本 Browser功能
lcd.browser_clear()
lcd.browser_set_content_max_length(1024)
lcd.browser_set_line_width(16)
# 设置滚动显示速度
lcd.browser_set_print_speed(3)
# 打印长文本
lcd.browser_print(long_text)
time.sleep(1)  # 等待1秒
# 根据行指针打印指定行内容到显示器指定行
lcd.browser_print_1line(3, 1)
time.sleep(1)  # 等待1秒
lcd.browser_print_1line(2, 0)
time.sleep(1)  # 等待1秒
# 同时打印显示2行
lcd.browser_print_2lines(0)
time.sleep(1)  # 等待1秒
# 从第1行起共10行，在显示器第2行进行单行翻滚显示
lcd.browser_scroll_1lines(0, 10, 1, speed=5)
time.sleep(1)  # 等待1秒
# 从第1行起共10行，双行翻滚显示
lcd.browser_scroll_2lines(0, 10, speed=2)
# 向上翻页
lcd.browser_page_up()
time.sleep(1)  # 等待1秒
# 向下翻页
lcd.browser_page_down()
time.sleep(1)  # 等待1秒