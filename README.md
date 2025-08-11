# LCD1602 MicroPython 直连控制库

本项目为 MicroPython 下的 LCD1602 (HD44780) 直连控制库，支持 4 位/8 位数据模式、灵活引脚映射、PWM 对比度/背光调节、文本浏览与滚动等高级功能。

## 主要特性

- 支持 4 位和 8 位数据传输模式
- 灵活的 LCD 引脚与 MCU GPIO 映射
- 支持 PWM 控制对比度（V0）和背光（BLA）
- 高级文本打印、行清除、光标控制、滚动显示
- 内置长文本浏览器（Browser），支持大文本分页、滚动、翻页显示
- 丰富的命令行调试与引脚状态输出

## 文件结构

- [`LCD1602.py`](LCD1602.py)：主库文件，功能最全，带详细注释
- [`LCD1602-min.py`](LCD1602-min.py)：精简版库文件
- [`test_lcd1602.py`](test_lcd1602.py)：主要功能测试与演示脚本

## 快速开始

### 1. 硬件连接

- LCD1602 的 D4-D7 分别连接到 MCU 的 GPIO4-GPIO7（4 位模式）
- 其余功能引脚（V0, RS, RW, E, BLA, BLK）按需连接
- 电源引脚连接好

### 2. 示例代码

以下为 [`test_lcd1602.py`](test_lcd1602.py) 的主要用法：

```python
from LCD1602 import LCD1602
import time

lcd = LCD1602()
lcd.set_data_trans_bits(4)
lcd.enable_pin("V0", 0)
lcd.enable_pin("RS", 1)
lcd.enable_pin("RW", 2)
lcd.enable_pin("E", 3)
lcd.enable_pin("D4", 4)
lcd.enable_pin("D5", 5)
lcd.enable_pin("D6", 6)
lcd.enable_pin("D7", 7)
lcd.init()
lcd.terminal_print_pins()
lcd.display_contrast(40)

lcd.print_line("Hello, World", 0)
time.sleep(1)
lcd.clear()
```

更多高级用法请参考 [`test_lcd1602.py`](test_lcd1602.py) 示例，包括：

- 单字符打印：`lcd.print_char("A")`
- 行打印与清除：`lcd.print_line("Text", 1)`、`lcd.clear_line(0)`
- 长文本分页/滚动：`lcd.print(long_text, 2)`、`lcd.scroll_line(text, 0, speed=3)`
- 光标控制：`lcd.cursor_move_left()`、`lcd.show_blink_cursor()`
- Browser 长文本浏览：`lcd.browser_print(long_text)`、`lcd.browser_page_up()`

## API 参考

详细 API 请见 [`LCD1602.py`](LCD1602.py) 注释，主要接口包括：

- `set_data_trans_bits(bits)`
- `enable_pin(pin_name, mcu_pin)`
- `print_line(text, line)`
- `print_char(char)`
- `clear()`, `clear_line(line)`
- `display_contrast(percent)`
- `backlight_brightness(percent)`
- `browser_print(text)`, `browser_page_up()`, `browser_page_down()`
- `cursor_move_left()`, `cursor_move_right()`, `cursor_move_up()`, `cursor_move_down()`

## 兼容性

- 适用于 MicroPython 支持的主控板（如 Raspberry Pi Pico 等）
- 需支持 `machine.Pin` 和 `machine.PWM` 模块

## 许可证

GPL-3.0 License

---

如需帮助或反馈建议，请联系：20739111@qq.com