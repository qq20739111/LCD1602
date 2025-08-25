from machine import Pin, PWM
import time
class LCD1602:
    def __init__(self, name = 'lcd1620'):
        self.version = "1.0.0"
        self.name = name
        self.__default_pins__ = ["VSS", "VDD", 
                             "V0", "RS", "RW", "E", 
                             "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", 
                             "BLA", "BLK"]
        self.__default_function_pins__ = self.__default_pins__[:6] + self.__default_pins__[-2:]
        self.__default_data_pins__ = self.__default_pins__[6:14]
        self.max_mcu_gpio_pin_num = 40
        self.mcu_gpio_pin_range = list(range(0, self.max_mcu_gpio_pin_num + 1))
        self.enabled_pins = {
        }
        self.bind_mcu_pins = {}
        self.__vss_to_mcu_pin__ = "GND"
        self.__vdd_to_mcu_pin__ = "VCC"
        self.__v0_to_mcu_pin__ = 1
        self.__rs_to_mcu_pin__ = 2
        self.__rw_to_mcu_pin__ = 3
        self.__e_to_mcu_pin__ = 4
        self.__data_pins_4bits__ = [5, 6, 7, 8]
        self.__data_pins_8bits__ = [5, 6, 7, 8, 9, 10, 11, 12]
        self.__bla_to_mcu_pin__ = "VCC"
        self.__blk_to_mcu_pin__ = "GND"
        self.v0_pwm = {
            "enable": True,
            "pin_name": self.__default_pins__[2],
            "freq": 1000,
            "duty_u16": 32768,
            "contrast_percent": 50,
        }
        self.bla_pwm = {
            "enable": False,
            "pin_name": self.__default_pins__[14],
            "freq": 1000,
            "duty_u16": 32768,
            "brightness_percent": 50,
        }
        self.settings = {
            "cursor_position": 0x00,
            "ac_auto_increase": True,
            "display_follow_cursor": False,
            "display_on": True,
            "cursor_visible": True,
            "cursor_blink": True,
            "data_trans_bits": 4,
            "display_lines": 2,
            "dot_matrix": 7,
        }
        self.command = {
            "LCD_CLEARDISPLAY": 0x01,
            "LCD_RETURNHOME": 0x02,
            "LCD_ENTRYMODESET_1": 0x04,
            "LCD_ENTRYMODESET_2": 0x05,
            "LCD_ENTRYMODESET_3": 0x06,
            "LCD_ENTRYMODESET_4": 0x07,
            "LCD_DISPLAYCONTROL_1": 0x08,
            "LCD_DISPLAYCONTROL_2": 0x09,
            "LCD_DISPLAYCONTROL_3": 0x0A,
            "LCD_DISPLAYCONTROL_4": 0x0B,
            "LCD_DISPLAYCONTROL_5": 0x0C,
            "LCD_DISPLAYCONTROL_6": 0x0D,
            "LCD_DISPLAYCONTROL_7": 0x0E,
            "LCD_DISPLAYCONTROL_8": 0x0F,
            "LCD_CURSORSHIFT_1": 0x10,
            "LCD_CURSORSHIFT_2": 0x14,
            "LCD_CURSORSHIFT_3": 0x18,
            "LCD_CURSORSHIFT_4": 0x1C,
            "LCD_FUNCTIONSET_4BIT_1LINE_5x7": 0x20,
            "LCD_FUNCTIONSET_4BIT_1LINE_5x10": 0x24,
            "LCD_FUNCTIONSET_4BIT_2LINE_5x7": 0x28,
            "LCD_FUNCTIONSET_4BIT_2LINE_5x10": 0x2C,
            "LCD_FUNCTIONSET_8BIT_1LINE_5x7": 0x30,
            "LCD_FUNCTIONSET_8BIT_1LINE_5x10": 0x34,
            "LCD_FUNCTIONSET_8BIT_2LINE_5x7": 0x38,
            "LCD_FUNCTIONSET_8BIT_2LINE_5x10": 0x3C,
            "LCD_SETCGRAMADDR": 0x40,
            "LCD_SETDDRAMADDR": 0x80,
        }
        self.browser = {
            "content": "",
            "content_length": 0,
            "content_max_length": 65536,
            "line_width": 16,
            "line_count": 0,
            "line_pointer": 0,
            "print_speed": 3
        }
        self.is_pin_ready = False
        self.is_write_ready = False
        self.is_read_ready = False
        self.init_by_default()
    def __str__(self):
        return f"LCD1602(name='{self.name}')"
    def __repr__(self):
        return "LCD1602()"
    def enable_pin(self, pin_name, mcu_pin_name):
        if pin_name not in self.__default_pins__:
            raise ValueError(f"Invalid pin name: {pin_name}. Valid names are: {', '.join(self.__default_pins__)}")
        if not isinstance(mcu_pin_name, (str, int)):
            raise ValueError(f"Invalid connected pin: {mcu_pin_name}. Must be a string or an integer.")
        if pin_name in self.__default_data_pins__ and not isinstance(mcu_pin_name, int) and not mcu_pin_name.isdigit():
            raise ValueError(f"Invalid connected pin: {mcu_pin_name}. Data pin {pin_name} must be connected to a GPIO number.")
        if isinstance(mcu_pin_name, str):
            if mcu_pin_name.isdigit():
                mcu_pin_name = int(mcu_pin_name)
        if isinstance(mcu_pin_name, int):
            if mcu_pin_name not in self.get_mcu_gpio_pins_list():
                raise ValueError(f"Invalid GPIO pin number: {mcu_pin_name}. Must be in range {self.get_mcu_gpio_pins_list()}.")
        self.enabled_pins[pin_name] = mcu_pin_name
        return True
    def enable_function_pin(self, pin_name, mcu_pin_name):
        if pin_name not in self.__default_function_pins__:
            raise ValueError(f"Invalid function pin name: {pin_name}. Valid names are: {', '.join(self.__default_function_pins__)}")
        return self.enable_pin(pin_name, mcu_pin_name)
    def enable_data_pin(self, pin_name, mcu_pin_name):
        if pin_name not in self.__default_data_pins__:
            raise ValueError(f"Invalid data pin name: {pin_name}. Valid names are: {', '.join(self.__default_data_pins__)}")
        return self.enable_pin(pin_name, mcu_pin_name)
    def enable_function_pins_by_default(self):
        for pin_name in self.__default_function_pins__:
            if pin_name in self.enabled_pins:
                self.disable_pin(pin_name)
        self.enable_pin(self.__default_pins__[0],  self.__vss_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[1],  self.__vdd_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[2],  self.__v0_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[3],  self.__rs_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[4],  self.__rw_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[5],  self.__e_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[14], self.__bla_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[15], self.__blk_to_mcu_pin__)
        return True
    def enable_data_pins_by_default (self):
        for pin_name in self.__default_data_pins__:
            if pin_name in self.enabled_pins:
                self.disable_pin(pin_name)
        if self.settings["data_trans_bits"] == 4:
            for i, pin in enumerate(self.__data_pins_4bits__):
                self.enabled_pins[self.__default_data_pins__[i + 4]] = pin
        elif self.settings["data_trans_bits"] == 8:
            for i, pin in enumerate(self.__data_pins_8bits__):
                self.enabled_pins[self.__default_data_pins__[i]] = pin
        else:
            raise ValueError("Invalid data transmit mode. Use '4bits' or '8bits'.")
        return True
    def disable_pin(self, pin_name):
        if pin_name not in self.__default_pins__:
            raise ValueError(f"Invalid pin name: {pin_name}. Valid names are: {', '.join(self.__default_pins__)}")
        if pin_name in self.enabled_pins:
            self.unbind_mcu_pin(pin_name)
            del self.enabled_pins[pin_name]
            return True
        else:
            return False
    def bind_mcu_pin(self, pin_name):
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        if self.enabled_pins[pin_name] not in self.get_mcu_gpio_pins_list():
            raise ValueError(f"Pin {pin_name} is not connected to a valid GPIO pin.")
        self.bind_mcu_pins[pin_name] = Pin(self.enabled_pins[pin_name], Pin.OUT)
        return True
    def bind_mcu_pwm_pin(self, pin_name, freq=1000, duty_u16=32768):
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        if self.enabled_pins[pin_name] not in self.get_mcu_gpio_pins_list():
            raise ValueError(f"Pin {pin_name} is not connected to a valid GPIO pin.")
        self.bind_mcu_pins[pin_name] = PWM(Pin(self.enabled_pins[pin_name]), freq=freq, duty_u16=duty_u16)
        return True
    def bind_function_pins_by_set(self):
        for pin_name in self.__default_function_pins__:
            if pin_name in self.enabled_pins:
                if self.enabled_pins[pin_name] in self.get_mcu_gpio_pins_list():
                    self.bind_mcu_pin(pin_name)
        return True
    def bind_data_pins_by_set(self):
        for pin_name in self.__default_data_pins__:
            if pin_name in self.enabled_pins:
                if self.enabled_pins[pin_name] in self.get_mcu_gpio_pins_list():
                    self.bind_mcu_pin(pin_name)
        return True
    def bind_pwm_pins_by_set(self):
        if self.v0_pwm["enable"]:
            self.unbind_mcu_pin(self.__default_pins__[2])
            self.bind_mcu_pwm_pin(self.__default_pins__[2], freq=self.v0_pwm["freq"], duty_u16=self.v0_pwm["duty_u16"])
        if self.bla_pwm["enable"]:
            self.unbind_mcu_pin(self.__default_pins__[14])
            self.bind_mcu_pwm_pin(self.__default_pins__[14], freq=self.bla_pwm["freq"], duty_u16=self.bla_pwm["duty_u16"])
        return True
    def unbind_mcu_pin(self, pin_name):
        if pin_name in self.bind_mcu_pins:
            del self.bind_mcu_pins[pin_name]
            return True
        else:
            return False
    def get_enabled_pins(self):
        return self.enabled_pins.copy()
    def get_enabled_pins_list(self):
        return [pin for pin in self.__default_pins__ if pin in self.enabled_pins]
    def get_enabled_function_pins(self):
        function_pins = self.__default_function_pins__
        return {pin: self.enabled_pins[pin] for pin in function_pins if pin in self.enabled_pins}
    def get_enabled_function_pins_list(self):
        return [pin for pin in self.__default_function_pins__ if pin in self.enabled_pins]
    def get_enabled_data_pins(self):
        data_pins = self.__default_data_pins__
        return {pin: self.enabled_pins[pin] for pin in data_pins if pin in self.enabled_pins}
    def get_enabled_data_pins_list(self):
        return [pin for pin in self.__default_data_pins__ if pin in self.enabled_pins]
    def get_mcu_gpio_pins_list(self):
        return self.mcu_gpio_pin_range
    def get_bind_mcu_pins(self):
        return self.bind_mcu_pins.copy()
    def get_bind_mcu_pins_list(self):
        return [pin for pin in self.__default_pins__ if pin in self.bind_mcu_pins]
    def get_bind_mcu_data_pins_list(self):
        return [pin for pin in self.__default_data_pins__ if pin in self.bind_mcu_pins]
    def terminal_print_pins(self):
        print(f"LCD1602 Instance {self.name} Pins:")
        for pin_name in self.__default_pins__:
            if pin_name in self.enabled_pins and pin_name in self.bind_mcu_pins:
                print(f"{pin_name}->{self.enabled_pins[pin_name]} (Pin Object: {self.bind_mcu_pins[pin_name]})")
            elif pin_name in self.enabled_pins:
                print(f"{pin_name}->{self.enabled_pins[pin_name]} (Pin Object: Not Bound)")
            elif pin_name in self.bind_mcu_pins:
                print(f"{pin_name}->Not Enabled (Pin Object: {self.bind_mcu_pins[pin_name]})")
            else:
                print(f"{pin_name}->Not Enabled")
        if not any(pin in self.enabled_pins for pin in self.__default_pins__):
            print("No pins enabled.")
        else:
            print("Pins enabled.")
        return None
    def terminal_print_function_pins(self):
        print(f"LCD1602 Instance {self.name} Function Pins:")
        function_pins = self.__default_function_pins__
        for pin_name in function_pins:
            if pin_name in self.enabled_pins and pin_name in self.bind_mcu_pins:
                print(f"{pin_name}->{self.enabled_pins[pin_name]} (Pin Object: {self.bind_mcu_pins[pin_name]})")
            elif pin_name in self.enabled_pins:
                print(f"{pin_name}->{self.enabled_pins[pin_name]} (Pin Object: Not Bound)")
            elif pin_name in self.bind_mcu_pins:
                print(f"{pin_name}->Not Enabled (Pin Object: {self.bind_mcu_pins[pin_name]})")
            else:
                print(f"{pin_name}->Not Enabled")
        if not any(pin in self.enabled_pins for pin in function_pins):
            print("No function pins enabled.")
        else:
            print("Function pins enabled.")
        return None
    def terminal_print_data_pins(self):
        print(f"LCD1602 Instance {self.name} Data Pins for {self.settings['data_trans_bits']}bits transmit mode:")
        data_pins = self.__default_data_pins__
        for pin_name in data_pins:
            if pin_name in self.enabled_pins and pin_name in self.bind_mcu_pins:
                print(f"{pin_name}->{self.enabled_pins[pin_name]} (Pin Object: {self.bind_mcu_pins[pin_name]})")
            elif pin_name in self.enabled_pins:
                print(f"{pin_name}->{self.enabled_pins[pin_name]} (Pin Object: Not Bound)")
            elif pin_name in self.bind_mcu_pins:
                print(f"{pin_name}->Not Enabled (Pin Object: {self.bind_mcu_pins[pin_name]})")
            else:
                print(f"{pin_name}->Not Enabled")
        if not any(pin in self.enabled_pins for pin in data_pins):
            print("No data pins enabled.")
        else:
            print("Data pins enabled.")
        return None
    def pulse_enable(self):
        self.bind_mcu_pins[self.__default_pins__[5]].value(1)
        time.sleep_us(1)
        self.bind_mcu_pins[self.__default_pins__[5]].value(0)
        time.sleep_us(100)
    def set_clear(self):
        self.send_byte_command(self.command["LCD_CLEARDISPLAY"])
        self.settings["cursor_position"] = 0x00
        time.sleep_ms(2)
        return True
    def clear(self):
        return self.set_clear()
    def clear_line(self, line=0):
        self.cursor_position(line, 0)
        for i in range(40):
            self.send_byte_data(0x20)
        self.cursor_position(line, 0)
        return True
    def set_cursor_return_home(self):
        self.send_byte_command(self.command["LCD_RETURNHOME"])
        self.settings["cursor_position"] = 0x00
        time.sleep_ms(2)
        return True
    def set_ac_auto_increase(self, mode=True):
        if mode not in [True, False]:
            return False
        else:
            self.settings["ac_auto_increase"] = mode
            self.set_ac_display_mode()
            return True
    def set_display_follow_cursor(self, mode=False):
        if mode not in [True, False]:
            return False
        else:
            self.settings["display_follow_cursor"] = mode
            self.set_ac_display_mode()
            return True
    def set_ac_display_mode(self):
        ac = int(bool(self.settings["ac_auto_increase"]))
        display = int(bool(self.settings["display_follow_cursor"]))
        cmds = [
            [self.command["LCD_ENTRYMODESET_1"], self.command["LCD_ENTRYMODESET_2"]],
            [self.command["LCD_ENTRYMODESET_3"], self.command["LCD_ENTRYMODESET_4"]],
        ]
        self.send_byte_command(cmds[ac][display])
        time.sleep_us(40)
        return True
    def set_display_on(self, mode=True):
        if mode not in [True, False]:
            return False
        else:
            self.settings["display_on"] = mode
            self.set_display_cursor_blink_mode()
            return True
    def set_cursor_visible(self, mode=True):
        if mode not in [True, False]:
            return False
        else:
            self.settings["cursor_visible"] = mode
            self.set_display_cursor_blink_mode()
            return True
    def set_cursor_blink(self, mode=True):
        if mode not in [True, False]:
            return False
        else:
            self.settings["cursor_blink"] = mode
            self.set_display_cursor_blink_mode()
            return True
    def set_display_cursor_blink_mode(self):
        display = int(bool(self.settings["display_on"]))
        cursor = int(bool(self.settings["cursor_visible"]))
        blink = int(bool(self.settings["cursor_blink"]))
        cmds = [
            self.command["LCD_DISPLAYCONTROL_1"],
            self.command["LCD_DISPLAYCONTROL_2"],
            self.command["LCD_DISPLAYCONTROL_3"],
            self.command["LCD_DISPLAYCONTROL_4"],
            self.command["LCD_DISPLAYCONTROL_5"],
            self.command["LCD_DISPLAYCONTROL_6"],
            self.command["LCD_DISPLAYCONTROL_7"],
            self.command["LCD_DISPLAYCONTROL_8"],
        ]
        idx = (display << 2) | (cursor << 1) | blink
        self.send_byte_command(cmds[idx])
        time.sleep_us(40)
        return True
    def set_data_trans_bits(self, bits=4):
        if bits not in [4, 8]:
            raise ValueError("Invalid data transmission mode. Use 4 or 8.")
        self.settings["data_trans_bits"] = bits
        self.set_data_lines_matrix_mode()
        self.is_pin_ready = False
        self.is_read_ready = False
        self.is_write_ready = False
        return True
    def set_display_lines(self, lines=2):
        if lines not in [1, 2]:
            return False
        else:
            self.settings["display_lines"] = lines
            self.set_data_lines_matrix_mode()
            return True
    def set_dot_matrix(self, size=7):
        if size not in [7, 10]:
            return False
        else:
            self.settings["dot_matrix"] = size
            self.set_data_lines_matrix_mode()
            return True
    def set_data_lines_matrix_mode(self):
        if self.settings["data_trans_bits"] == 4:
            if self.settings["display_lines"] == 1:
                if self.settings["dot_matrix"] == 7:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_4BIT_1LINE_5x7"])
                elif self.settings["dot_matrix"] == 10:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_4BIT_1LINE_5x10"])
            else:
                if self.settings["dot_matrix"] == 7:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_4BIT_2LINE_5x7"])
                elif self.settings["dot_matrix"] == 10:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_4BIT_2LINE_5x10"])
        elif self.settings["data_trans_bits"] == 8:
            if self.settings["display_lines"] == 1:
                if self.settings["dot_matrix"] == 7:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_8BIT_1LINE_5x7"])
                elif self.settings["dot_matrix"] == 10:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_8BIT_1LINE_5x10"])
            elif self.settings["display_lines"] == 2:
                if self.settings["dot_matrix"] == 7:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_8BIT_2LINE_5x7"])
                elif self.settings["dot_matrix"] == 10:
                    self.send_byte_command(self.command["LCD_FUNCTIONSET_8BIT_2LINE_5x10"])
        time.sleep_us(40)
        return True
    def send_bits(self, value, bits_count=4):
        if not self.is_pin_ready:
            raise ValueError("Pin is not ready. Please initialize the pin first.")
        data_pins_list = self.get_bind_mcu_data_pins_list()
        if bits_count != len(data_pins_list):
            raise ValueError("Invalid bits count. Please check the data pins configuration.")
        self.bind_mcu_pins[self.__default_pins__[4]].value(0)
        for i in range(bits_count):
            self.bind_mcu_pins[data_pins_list[i]].value((value >> i) & 1)
        self.pulse_enable()
        return True
    def send_byte(self, value):
        if not isinstance(value, int):
            raise ValueError("Invalid value type. Expected an integer.")
        if self.settings["data_trans_bits"] == 4:
            self.send_bits(value >> 4, 4)
            self.send_bits(value & 0x0F, 4)
        elif self.settings["data_trans_bits"] == 8:
            self.send_bits(value, 8)
        else:
            raise ValueError("Invalid data transmission mode. Use '4bits' or '8bits'.")
        return True
    def send_byte_command(self, value):
        self.bind_mcu_pins[self.__default_pins__[3]].value(0)
        self.send_byte(value)
        return True
    def send_byte_data(self, value):
        self.bind_mcu_pins[self.__default_pins__[3]].value(1)
        self.send_byte(value)
        self.cursor_position_increase()
        return True
    def print_char(self, char):
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("Invalid character. Expected a single character string.")
        self.send_byte_data(ord(char))
        return True
    def print_line(self, text, line=0):
        if line not in [0, 1]:
            raise ValueError("Invalid line number. Line must be 0 or 1.")
        if not self.is_write_ready:
            raise ValueError("Write is not ready. Please initialize the write first.")
        self.clear_line(line)
        for char in text[:40]:
            self.send_byte_data(ord(char))
        return True
    def print(self, text, speed=1, line_width=16):
        if line_width < 1 or line_width > 40:
            line_width = 16
        pages = [text[i:i + line_width] for i in range(0, len(text), line_width)]
        interval = 1 / speed
        pages_lens = len(pages)
        for lp in range(pages_lens):
            if lp + 1 < pages_lens:
                self.print_line(pages[lp], 0)
                self.print_line(pages[lp + 1], 1)
            else:
                self.print_line(pages[lp], 0)
                self.clear_line(1)
            time.sleep(interval)
        self.set_clear()
        return True
    def scroll_line(self, text, line=0, speed=3):
        if not self.is_write_ready:
            raise ValueError("Write is not ready. Please initialize the write first.")
        self.cursor_position(line, 0)
        paded_text = " " * 16 + text + " " * 16
        interval = 1 / speed
        for i in range(len(paded_text) - 16):
            text_slice = paded_text[i:i + 16]
            self.print_line(text_slice, line)
            time.sleep(interval)
        self.clear_line(line)
        return True
    def display_on(self):
        return self.set_display_on(True)
    def display_off(self):
        return self.set_display_on(False)
    def hide_blink_cursor(self):
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_5"]) 
        return True
    def show_blink(self):
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_6"])
        return True
    def show_cursor(self):
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_7"])
        return True
    def show_blink_cursor(self):
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_8"])
        return True
    def cursor_home(self):
        return self.set_cursor_return_home()
    def cursor_position(self, row, column):
        if not (0 <= row < 2):
            raise ValueError("Invalid row position. Row must be 0 or 1.")
        if not (0 <= column < 40):
            raise ValueError("Invalid column position. Column must be between 0 and 39.")
        self.settings["cursor_position"] = (row * 0x40) + column
        self.send_byte_command(self.command["LCD_SETDDRAMADDR"] | self.settings["cursor_position"])
        return True
    def cursor_position_decrease(self):
        if self.settings["cursor_position"] < 0x28:
            self.settings["cursor_position"] -= 1
        elif self.settings["cursor_position"] == 0x00:
            self.settings["cursor_position"] = 0x67
        elif self.settings["cursor_position"] < 0x68:
            self.settings["cursor_position"] -= 1
        elif self.settings["cursor_position"] == 0x40:
            self.settings["cursor_position"] = 0x27
        return True
    def cursor_position_increase(self):
        if self.settings["cursor_position"] < 0x27:
            self.settings["cursor_position"] += 1
        elif self.settings["cursor_position"] == 0x27:
            self.settings["cursor_position"] = 0x40
        elif self.settings["cursor_position"] < 0x67:
            self.settings["cursor_position"] += 1
        elif self.settings["cursor_position"] == 0x67:
            self.settings["cursor_position"] = 0x00
        return True
    def cursor_move_left(self):
        if self.settings["cursor_position"] & 0x3F > 0:
            self.settings["cursor_position"] -= 1
            self.send_byte_command(self.command["LCD_CURSORSHIFT_1"])
        elif self.settings["cursor_position"] & 0x3F == 0:
            self.settings["cursor_position"] = self.settings["cursor_position"] + 0x27
            self.cursor_position((self.settings["cursor_position"] & 0x40) >> 6, 0x27)
        return True
    def cursor_move_right(self):
        if self.settings["cursor_position"] & 0x3F < 0x27:
            self.settings["cursor_position"] += 1
            self.send_byte_command(self.command["LCD_CURSORSHIFT_2"])
        elif self.settings["cursor_position"] & 0x3F == 0x27:
            self.settings["cursor_position"] = self.settings["cursor_position"] - 0x27
            self.cursor_position((self.settings["cursor_position"] & 0x40) >> 6, 0x00)
        return True
    def cursor_move_up(self):
        if self.settings["cursor_position"] >= 0x40:
            self.settings["cursor_position"] -= 0x40
            self.send_byte_command(self.command["LCD_SETDDRAMADDR"] | self.settings["cursor_position"])
        return True
    def cursor_move_down(self):
        if self.settings["cursor_position"] < 40:
            self.settings["cursor_position"] += 0x40
            self.send_byte_command(self.command["LCD_SETDDRAMADDR"] | self.settings["cursor_position"])
        return True
    def browser_set_content_max_length(self, content_max_length=1024):
        self.browser["content_max_length"] = content_max_length
        return True
    def browser_set_buffer_size(self, content_max_length=1024):
        return self.browser_set_content_max_length(content_max_length)
    def browser_get_content_max_length(self):
        return self.browser["content_max_length"]
    def browser_get_buffer_size(self):
        return self.browser_get_content_max_length()
    def browser_get_content(self):
        return self.browser["content"]
    def browser_get_content_length(self):
        return self.browser["content_length"]
    def browser_set_line_width(self, line_width=16):
        if line_width < 1 or line_width > 40:
            return False
        self.browser["line_width"] = line_width
        self.browser["line_count"] = (self.browser["content_length"] + line_width - 1) // line_width
        self.browser["line_pointer"] = 0
        return True
    def browser_get_line_width(self):
        return self.browser["line_width"]
    def browser_get_line_count(self):
        return self.browser["line_count"]
    def browser_set_line_pointer(self, line_pointer=0):
        if line_pointer < 0:
            line_pointer = 0
        elif line_pointer >= self.browser["line_count"]:
            line_pointer = self.browser["line_count"] - 1
        self.browser["line_pointer"] = line_pointer
        return True
    def browser_get_line_pointer(self):
        return self.browser["line_pointer"]
    def browser_set_print_speed(self, print_speed=3):
        self.browser["print_speed"] = print_speed
        return True
    def browser_clear(self):
        self.browser["content"] = ""
        self.browser["content_length"] = 0
        self.browser["line_count"] = 0
        self.browser["line_pointer"] = 0
        return True
    def browser_get_1line(self, line_pointer=None):
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        if 0 <= line_pointer <= self.browser["line_count"] - 1:
            start = line_pointer * self.browser["line_width"]
            end = start + self.browser["line_width"]
            return self.browser["content"][start:end] if start < self.browser["content_length"] else ""
        else:
            return ""
    def browser_print_1line(self, line_pointer=None, line=0):
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        content = self.browser_get_1line(line_pointer)
        self.print_line(content, line)
        return True
    def browser_print_2lines(self, line_pointer=None):
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        content0 = self.browser_get_1line(line_pointer)
        content1 = self.browser_get_1line(line_pointer + 1)
        self.print_line(content0, 0)
        self.print_line(content1, 1)
        return True
    def browser_line_up(self):
        self.browser_set_line_pointer(self.browser_get_line_pointer() - 1)
        self.browser_print_2lines()
        return True
    def browser_line_down(self):
        self.browser_set_line_pointer(self.browser_get_line_pointer() + 1)
        self.browser_print_2lines()
        return True
    def browser_page_up(self):
        self.browser_set_line_pointer(self.browser_get_line_pointer() - 2)
        self.browser_print_2lines()
        return True
    def browser_page_down(self):
        self.browser_set_line_pointer(self.browser_get_line_pointer() + 2)
        self.browser_print_2lines()
        return True
    def browser_scroll_1lines(self, line_pointer=None, count=1, line=0, speed=None):
        if count < 1:
            return False
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        if line_pointer < 0:
            line_pointer = 0
        if line_pointer >= self.browser["line_count"]:
            line_pointer = self.browser["line_count"] - 1
        start_line = line_pointer
        end_line = start_line + count
        if end_line > self.browser["line_count"]:
            end_line = self.browser["line_count"]
        interval = 1 / (speed if speed is not None else self.browser["print_speed"])
        for lp in range(start_line, end_line):
            self.browser_print_1line(lp, line)
            time.sleep(interval)
        self.clear_line(line)
        return True
    def browser_scroll_2lines(self, line_pointer=None, count=1, speed=None):
        if count < 1:
            return False
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        if line_pointer < 0:
            line_pointer = 0
        if line_pointer >= self.browser["line_count"]:
            line_pointer = self.browser["line_count"] - 1
        start_line = line_pointer
        end_line = start_line + count
        if end_line > self.browser["line_count"]:
            end_line = self.browser["line_count"]
        interval = 1 / (speed if speed is not None else self.browser["print_speed"])
        for lp in range(start_line, end_line):
            if lp + 1 < end_line:
                self.browser_print_2lines(lp)
            else:
                self.browser_print_1line(lp)
                self.clear_line(1)
            time.sleep(interval)
        self.set_clear()
        return True
    def browser_write(self, text):
        text_length = len(text)
        if text_length > self.browser["content_max_length"]:
            raise ValueError("Content length exceeds maximum limit.")
        if self.browser["content_length"] + text_length > self.browser["content_max_length"]:
            del_length = (self.browser["content_length"] + text_length) - self.browser["content_max_length"]
            self.browser["content"] = self.browser["content"][del_length:]
        self.browser["content"] += text
        self.browser["content_length"] = len(self.browser["content"])
        self.browser["line_count"] = (self.browser["content_length"] + self.browser["line_width"] - 1) // self.browser["line_width"]
        self.browser["line_pointer"] = self.browser["line_count"] - 1
        text_line_count = (text_length + self.browser["line_width"] - 1) // self.browser["line_width"]
        self.browser_scroll_2lines(self.browser["line_pointer"] - text_line_count + 1, text_line_count, self.browser["print_speed"])
        return True
    def browser_print(self, text):
        return self.browser_write(text)
    def percent_to_pwm_duty_u16(self, percent):
        if not (0 <= percent <= 100):
            raise ValueError("Percent must be between 0 and 100.")
        return int(percent * 65535 / 100)
    def display_contrast(self, percent):
        if not self.v0_pwm["enable"]:
            raise ValueError("V0 PWM control is not enabled. Please enable it first.")
        pin_name = self.v0_pwm["pin_name"]
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        if pin_name not in self.bind_mcu_pins:
            raise ValueError(f"Pin {pin_name} is not initialized. Please bind it first.")
        if not isinstance(self.bind_mcu_pins[pin_name], PWM):
            raise ValueError(f"Pin {pin_name} is not a PWM pin.")
        if not (0 <= percent <= 100):
            raise ValueError("Contrast percent must be between 0 and 100.")
        duty = self.percent_to_pwm_duty_u16(percent)
        self.v0_pwm["duty_u16"] = duty
        self.v0_pwm["contrast_percent"] = percent
        self.bind_mcu_pins[pin_name].duty_u16(duty)
        return True
    def backlight_brightness(self, percent):
        if not self.bla_pwm["enable"]:
            raise ValueError("BLA PWM control is not enabled. Please enable it first.")
        pin_name = self.bla_pwm["pin_name"]
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        if pin_name not in self.bind_mcu_pins:
            raise ValueError(f"Pin {pin_name} is not initialized. Please bind it first.")
        if not isinstance(self.bind_mcu_pins[pin_name], PWM):
            raise ValueError(f"Pin {pin_name} is not a PWM pin.")
        if not (0 <= percent <= 100):
            raise ValueError("Backlight brightness percent must be between 0 and 100.")
        duty = self.percent_to_pwm_duty_u16(percent)
        self.bla_pwm["duty_u16"] = duty
        self.bla_pwm["brightness_percent"] = percent
        self.bind_mcu_pins[pin_name].duty_u16(duty)
        return True
    def init_lcd_write(self):
        time.sleep_ms(15)
        self.set_data_lines_matrix_mode()
        time.sleep_ms(5)
        self.set_data_lines_matrix_mode()
        time.sleep_us(100)
        self.set_data_lines_matrix_mode()
        time.sleep_us(40)
        self.set_data_lines_matrix_mode()
        self.set_clear()
        self.set_cursor_return_home()
        self.set_ac_display_mode()
        self.set_display_cursor_blink_mode()
        self.is_write_ready = True
        return True
    def init_default_pins(self):
        self.is_pin_ready = False
        self.enable_function_pins_by_default()
        self.bind_function_pins_by_set()
        self.enable_data_pins_by_default()
        self.bind_data_pins_by_set()
        self.bind_pwm_pins_by_set()
        self.is_pin_ready = True
        return True
    def init_pins(self):
        self.is_pin_ready = False
        self.bind_function_pins_by_set()
        self.bind_data_pins_by_set()
        self.bind_pwm_pins_by_set()
        self.is_pin_ready = True
        return True
    def init_by_default(self):
        self.init_default_pins()
        self.init_lcd_write()
        return True
    def init(self):
        self.init_pins()
        self.init_lcd_write()
        return True