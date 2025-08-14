from machine import Pin, PWM
import time

class LCD1602:
    """
    MicroPython LCD1602 HD44780 直连控制模块
    MicroPython LCD1602 HD44780 Direct Control Module
    hi@leilei.name
    2025 by LeiLei
    """
    def __init__(self, name = 'lcd1620'):
        """
        通过名称初始化 LCD1602 实例
        Initialize LCD1602 instance with a name.
        并初始化为默认配置
        Initialize with default configuration.
        :param name: 实例名称，默认为 'lcd1620'
        """
        # 类版本号
        self.version = "1.0.0"
        # 实例名称
        self.name = name

        # ########################################
        # 关于初始化引脚Pin的相关配置
        #

        # 定义 LCD1602 的引脚
        # 配置默认LCD引脚名称列表
        self.__default_pins__ = ["VSS", "VDD", 
                             "V0", "RS", "RW", "E", 
                             "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", 
                             "BLA", "BLK"]
        # 生成默认LCD功能引脚名称列表
        self.__default_function_pins__ = self.__default_pins__[:6] + self.__default_pins__[-2:]
        # 生成默认LCD数据引脚名称列表
        self.__default_data_pins__ = self.__default_pins__[6:14]

        # 配置所连接MCU可用引脚的范围列表
        # self.mcu_gpio_pin_range = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        # 配置所连接MCU引脚所支持的最大GPIO编号，并根据MCU的最大GPIO编号生成范围列表
        self.max_mcu_gpio_pin_num = 40
        self.mcu_gpio_pin_range = list(range(0, self.max_mcu_gpio_pin_num + 1))

        # 存储已启用的LCD引脚的名称和对应连接的MCU的引脚值（编号或名称）的字典 用于表示LCD引脚是否启用
        self.enabled_pins = {
            # "VSS": "GND", # Pin1 Connect to GND. 接电源地
            # "VDD": "VCC", # Pin2  Connetct to VCC. 接电源正
            # "V0": "1", # Pin3 Connetct to GPIO1. 功能引脚，接PWM引脚，通过偏置电压调节屏幕对比度
            # "RS": "2", #  Pin4 Connetct to GPIO2. 功能引脚，数据/命令选择，高电平传数据，低电平传命令
            # "RW": "3", #  Pin5 Connetct to GPIO3. 功能引脚，读/写选择，高电平读操作，低电平写操作
            # "E": "4", #  Pin6 Connetct to GPIO4. 功能引脚，使能信号，由高电平跳变低电平时LCD1602执行操作
            # "D0": "5", #  Pin7-14 Connetct to GPIO5 - GPIO12. 低位数据引脚，根据配置初始化值
            # "D1": "6", #  Pin7-14 Connetct to GPIO5 - GPIO12. 低位数据引脚，根据配置初始化值
            # "D2": "7", #  Pin7-14 Connetct to GPIO5 - GPIO12. 低位数据引脚，根据配置初始化值
            # "D3": "8", #  Pin7-14 Connetct to GPIO5 - GPIO12. 低位数据引脚，根据配置初始化值
            # "D4": "9", #  Pin7-14 Connetct to GPIO5 - GPIO12. 高位数据引脚，根据配置初始化值
            # "D5": "10", #  Pin7-14 Connetct to GPIO5 - GPIO12. 高位数据引脚，根据配置初始化值
            # "D6": "11", #  Pin7-14 Connetct to GPIO5 - GPIO12. 高位数据引脚，根据配置初始化值
            # "D7": "12", #  Pin7-14 Connetct to GPIO5 - GPIO12. 高位数据引脚，根据配置初始化值
            # "BLA": "VCC", #  Pin15 Connetct to VCC. 背光电源正极
            # "BLK": "GND", #  Pin16 Connetct to GND. 背光电源负极
        }

        # 存储LCD引脚名称和对应绑定了MCU引脚的 Pin 对象的字典 用于实际操作引脚
        self.bind_mcu_pins = {}

        # 配置LCD电源引脚连接到MCU引脚的名称或编号
        # VSS
        self.__vss_to_mcu_pin__ = "GND"
        # VDD
        self.__vdd_to_mcu_pin__ = "VCC"
        
        # 配置LCD【功能引脚】所连接MCU的GPIO编号
        # V0
        self.__v0_to_mcu_pin__ = 1  # V0 引脚连接到 GPIO1
        # RS
        self.__rs_to_mcu_pin__ = 2  # RS 引脚连接到 GPIO2
        # RW
        self.__rw_to_mcu_pin__ = 3  # RW 引脚连接到 GPIO3
        # E
        self.__e_to_mcu_pin__ = 4  # E 引脚连接到 GPIO4

        # 根据LCD数据传输模式，配置LCD【数据引脚】所连接MCU的GPIO引脚编号 按引脚编号顺序设置
        # 4位模式：D4-D7. 设置"4bits"数据传输模式LCD引脚（高4位）所连接MCU的GPIO引脚
        self.__data_pins_4bits__ = [5, 6, 7, 8] # 连接到MCU GPIO5 - GPIO8
        # 8位模式：D0-D7. 设置"8bits"数据传输模式LCD引脚（全8位）所连接MCU的GPIO引脚
        self.__data_pins_8bits__ = [5, 6, 7, 8, 9, 10, 11, 12] # 连接到MCU GPIO5 - GPIO12

        # 配置背光电源引脚连接名称
        # BLA
        # 如果BLA引脚需要PWM控制，则设置连接到GPIO数字编号引脚，例如 self.__bla_to_mcu_pin__ = 13
        self.__bla_to_mcu_pin__ = "VCC"  # BLA 引脚连接到 VCC
        # BLK
        self.__blk_to_mcu_pin__ = "GND"  # BLK 引脚连接到 GND

        # 配置PWM引脚
        # V0 通过PWM调节显示对比度，如果V0引脚需要PWM控制，则设置为：{"enable" : True}
        self.v0_pwm = {
            "enable": True,                        # 是否启用V0 PWM控制
            "pin_name": self.__default_pins__[2],  # 取得LCD V0 引脚名称
            "freq": 1000,                          # PWM 频率
            "duty_u16": 32768,                     # 默认占空比为50%
            "contrast_percent": 50,                # 默认显示对比度为50%
        }
        # BLA 通过PWM调节背光亮度，如果BLA引脚需要PWM控制，则设置为：{"enable" : True}
        self.bla_pwm = {
            "enable": False,                       # 是否启用BLA PWM控制
            "pin_name": self.__default_pins__[14], # 取得LCD BLA 引脚名称
            "freq": 1000,                          # PWM 频率
            "duty_u16": 32768,                     # 默认占空比为50%
            "brightness_percent": 50,              # 默认背光亮度为50%
        }

        # ########################################
        # 关于LCD的基本设置和互动方式的相关配置
        #

        self.settings = {
            "cursor_position": 0x00,  # 默认光标位置，作为光标指示器
            "ac_auto_increase": True,  # 光标地址自动计数器默认增加（True）还是减少（False）
            "display_follow_cursor": False,  # 默认是否开启显示自动跟随移动
            "display_on": True,  # 默认是否开启屏幕显示
            "cursor_visible": True,  # 默认是否显示光标
            "cursor_blink": True,  # 默认是否开启光标闪烁
            "data_trans_bits": 4,  # 默认数据传输位数，4位或8位
            "display_lines": 2,  # 默认显示行数，1或2
            "dot_matrix": 7,  # 默认点阵大小设置为7（5x7），可选：10（5x10）
        }

        # 定义LCD1602命令集
        self.command = {
            "LCD_CLEARDISPLAY": 0x01, #清屏 清除DDRAM数据和AC值
            "LCD_RETURNHOME": 0x02, #光标和屏幕归位 AC=0
            "LCD_ENTRYMODESET_1": 0x04, #读写操作后，光标AC自动减1，屏幕不移
            "LCD_ENTRYMODESET_2": 0x05, #读写操作后，光标AC自动减1，屏幕左移
            "LCD_ENTRYMODESET_3": 0x06, #读写操作后，光标AC自动加1，屏幕不移
            "LCD_ENTRYMODESET_4": 0x07, #读写操作后，光标AC自动加1，屏幕右移
            "LCD_DISPLAYCONTROL_1": 0x08, #关显示，关光标，关闪烁
            "LCD_DISPLAYCONTROL_2": 0x09, #关显示，关光标，开闪烁
            "LCD_DISPLAYCONTROL_3": 0x0A, #关显示，开光标，关闪烁
            "LCD_DISPLAYCONTROL_4": 0x0B, #关显示，开光标，开闪烁
            "LCD_DISPLAYCONTROL_5": 0x0C, #开显示，关光标，关闪烁
            "LCD_DISPLAYCONTROL_6": 0x0D, #开显示，关光标，开闪烁
            "LCD_DISPLAYCONTROL_7": 0x0E, #开显示，开光标，关闪烁
            "LCD_DISPLAYCONTROL_8": 0x0F, #开显示，开光标，开闪烁
            "LCD_CURSORSHIFT_1": 0x10, #手动移动光标，光标向左移1位，AC值减1
            "LCD_CURSORSHIFT_2": 0x14, #手动移动光标，光标向右移1位，AC值加1
            "LCD_CURSORSHIFT_3": 0x18, #手动移动屏幕，屏幕内容向左移1位，光标不动
            "LCD_CURSORSHIFT_4": 0x1C, #手动移动屏幕，屏幕内容向右移1位，光标不动
            "LCD_FUNCTIONSET_4BIT_1LINE_5x7": 0x20, #设置为4bits数据接口，一行显示，5x7字符点阵
            "LCD_FUNCTIONSET_4BIT_1LINE_5x10": 0x24, #设置为4bits数据接口，一行显示，5x10字符点阵
            "LCD_FUNCTIONSET_4BIT_2LINE_5x7": 0x28, #设置为4bits数据接口，两行显示，5x7字符点阵
            "LCD_FUNCTIONSET_4BIT_2LINE_5x10": 0x2C, #设置为4bits数据接口，两行显示，5x10字符点阵
            "LCD_FUNCTIONSET_8BIT_1LINE_5x7": 0x30, #设置为8bits数据接口，一行显示，5x7字符点阵
            "LCD_FUNCTIONSET_8BIT_1LINE_5x10": 0x34, #设置为8bits数据接口，一行显示，5x10字符点阵
            "LCD_FUNCTIONSET_8BIT_2LINE_5x7": 0x38, #设置为8bits数据接口，两行显示，5x7字符点阵
            "LCD_FUNCTIONSET_8BIT_2LINE_5x10": 0x3C, #设置为8bits数据接口，两行显示，5x10字符点阵
            "LCD_SETCGRAMADDR": 0x40, #设置CGRAM自定义字符地址为：0x4X（0b_01**_****）
            "LCD_SETDDRAMADDR": 0x80, #设置下一个要存入数据的DDRAM地址为：0x8X（0b_1***_****）
        }

        # ########################################
        # 关于长文本编辑器Browser的相关配置
        #

        # 长文本浏览器
        self.browser = {
            "content": "", # 存储文本内容的缓冲区
            "content_length": 0, # 内容长度从1开始计数
            "content_max_length": 65536,
            "line_width": 16,
            "line_count": 0, # 行数从1开始计数
            "line_pointer": 0, # 行指针从0开始计数
            "print_speed": 3 # 默认打印速度为3次每秒
        }

        # ########################################
        # LCD1602 实例的初始化状态
        #

        # 是否准备好引脚
        self.is_pin_ready = False
        # 是否准备好写入数据
        self.is_write_ready = False
        # 是否准备好读取数据
        self.is_read_ready = False

        # 启动默认初始化
        self.init_by_default()
    # end of __init__
    
    # Class 的字符串表示
    def __str__(self):
        return f"LCD1602(name='{self.name}')"
    
    # Class 的调试字符串表示
    def __repr__(self):
        return "LCD1602()"

    # ########################################
    # 以下是关于引脚Pin的设置和初始化的方法
    #

    # 动态启用LCD引脚并设置所连接的MCU引脚值
    def enable_pin(self, pin_name, mcu_pin_name):
        """
        动态启用并设置 LCD1602 实例的引脚连接
        Dynamically enable and set the pin connection of the LCD1602 instance.
        :param pin_name: 要设置的LCD引脚名称
        The name of the pin to set.
        :param mcu_pin_name: 所连接MCU的引脚值，为编号或名称，可以是字符串或整数，但数据引脚对应的引脚值必须是数字
        The pin value connected to the MCU, can be a string or an integer, but data pins must be numeric.
        :return: 如果设置成功，返回 True
        Returns True if the setting is successful.
        :raises ValueError: 如果LCD引脚名称无效或所连接的MCU引脚值不符合要求，则抛出异常
        Raises ValueError if the pin name is invalid or the connected MCU pin value does not meet the requirements.
        """
        # 检查LCD引脚名称是否被定义
        if pin_name not in self.__default_pins__:
            raise ValueError(f"Invalid pin name: {pin_name}. Valid names are: {', '.join(self.__default_pins__)}")
        # 检查所连接的MCU引脚值是否为str或int
        if not isinstance(mcu_pin_name, (str, int)):
            raise ValueError(f"Invalid connected pin: {mcu_pin_name}. Must be a string or an integer.")
        # 检查设置LCD引脚名称，如果为数据引脚，所连接的MCU引脚值必须是数字
        if pin_name in self.__default_data_pins__ and not isinstance(mcu_pin_name, int) and not mcu_pin_name.isdigit():
            raise ValueError(f"Invalid connected pin: {mcu_pin_name}. Data pin {pin_name} must be connected to a GPIO number.")
        # 如果所连接的MCU引脚值是字符串
        if isinstance(mcu_pin_name, str):
            # 如果所连接的MCU引脚值为数字字符串，则转换为int
            if mcu_pin_name.isdigit():
                mcu_pin_name = int(mcu_pin_name)
        # 如果所连接的MCU引脚值是整数，则检查是否在有效范围内
        if isinstance(mcu_pin_name, int):
            # 检查是否为有效的GPIO编号
            if mcu_pin_name not in self.get_mcu_gpio_pins_list():
                raise ValueError(f"Invalid GPIO pin number: {mcu_pin_name}. Must be in range {self.get_mcu_gpio_pins_list()}.")
        # 设置LCD引脚所连接的MCU引脚值
        self.enabled_pins[pin_name] = mcu_pin_name
        return True
    # end of enable_pin

    # 动态启用LCD功能引脚并设置所连接的MCU引脚值
    def enable_function_pin(self, pin_name, mcu_pin_name):
        """
        动态启用并设置 LCD1602 实例的功能引脚连接
        Dynamically enable and set the function pin connection of the LCD1602 instance.
        :param pin_name: 要设置的LCD功能引脚名称
        The name of the function pin to set.
        """
        # 检查LCD功能引脚名称是否被定义
        if pin_name not in self.__default_function_pins__:
            raise ValueError(f"Invalid function pin name: {pin_name}. Valid names are: {', '.join(self.__default_function_pins__)}")
        # 调用enable_pin方法启用功能引脚
        return self.enable_pin(pin_name, mcu_pin_name)

    # 动态启用LCD数据引脚并设置所连接的MCU引脚值
    def enable_data_pin(self, pin_name, mcu_pin_name):
        """
        动态启用并设置 LCD1602 实例的数据引脚连接
        Dynamically enable and set the data pin connection of the LCD1602 instance.
        :param pin_name: 要设置的数据引脚名称
        The name of the data pin to set.
        :param mcu_pin_name: 所连接MCU的引脚值必须是数字
        The pin value connected to the MCU must be numeric.
        """
        # 检查LCD数据引脚名称是否被定义
        if pin_name not in self.__default_data_pins__:
            raise ValueError(f"Invalid data pin name: {pin_name}. Valid names are: {', '.join(self.__default_data_pins__)}")
        # 调用enable_pin方法启用数据引脚
        return self.enable_pin(pin_name, mcu_pin_name)

    # 根据LCD默认设置启用功能引脚
    def enable_function_pins_by_default(self):
        """
        根据 LCD1602 实例的功能引脚默认设置启用功能引脚
        Enable function pins of the LCD1602 instance based on the default function pin settings.
        :return: 如果设置成功，返回 True
        Returns True if the setting is successful.
        """
        # 清空所有已启用的功能引脚
        for pin_name in self.__default_function_pins__:
            if pin_name in self.enabled_pins:
                self.disable_pin(pin_name)  # 删除绑定的 Pin 对象并停用引脚

        # 根据默认设置的启用所有功能引脚
        self.enable_pin(self.__default_pins__[0],  self.__vss_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[1],  self.__vdd_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[2],  self.__v0_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[3],  self.__rs_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[4],  self.__rw_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[5],  self.__e_to_mcu_pin__)
        # 启用背光引脚
        self.enable_pin(self.__default_pins__[14], self.__bla_to_mcu_pin__)
        self.enable_pin(self.__default_pins__[15], self.__blk_to_mcu_pin__)
        # 返回设置成功
        return True

    # 根据LCD传输模式设置启用数据引脚
    def enable_data_pins_by_default (self):
        """
        根据 LCD1602 实例的数据传输模式设置启用默认数据引脚
        Enable default data pins of the LCD1602 instance based on the data transmission mode.
        :return: 如果设置成功，返回 True
        Returns True if the setting is successful.
        """
        # 清空所有已启用的数据引脚
        for pin_name in self.__default_data_pins__:
            if pin_name in self.enabled_pins:
                self.disable_pin(pin_name)  # 删除绑定的 Pin 对象并停用引脚

        # 基于传输模式启用对应的数据引脚，4bits 模式使用 D4-D7 引脚，8bits 模式使用 D0-D7 引脚
        # D0-D3 为低位数据引脚，D4-D7 为高位数据引脚
        if self.settings["data_trans_bits"] == 4:
            for i, pin in enumerate(self.__data_pins_4bits__):
                self.enabled_pins[self.__default_data_pins__[i + 4]] = pin
        elif self.settings["data_trans_bits"] == 8:
            for i, pin in enumerate(self.__data_pins_8bits__):
                self.enabled_pins[self.__default_data_pins__[i]] = pin
        else:
            raise ValueError("Invalid data transmit mode. Use '4bits' or '8bits'.")
        return True
        
    # 停用LCD引脚并动态断开引脚的连接
    def disable_pin(self, pin_name):
        """
        停用并断开 LCD1602 实例的引脚连接
        Disable and disconnect the pin connection of the LCD1602 instance.
        :param pin_name: 要断开的LCD引脚名称
        The name of the pin to disconnect.
        :return: 如果断开成功，返回 True
        Returns True if the disconnection is successful.
        :raises ValueError: 如果LCD引脚名称无效，则抛出异常
        Raises ValueError if the pin name is invalid.
        """
        # 检查LCD引脚名称是否被定义
        if pin_name not in self.__default_pins__:
            raise ValueError(f"Invalid pin name: {pin_name}. Valid names are: {', '.join(self.__default_pins__)}")
        # 检查引脚是否已启用
        if pin_name in self.enabled_pins:
            self.unbind_mcu_pin(pin_name)  # 删除绑定的 Pin 对象
            del self.enabled_pins[pin_name]   # 删除引脚连接
            return True
        else:
            return False
    # end of disable_pin

    # 根据LCD引脚名称创建并绑定Pin对象
    def bind_mcu_pin(self, pin_name):
        """
        根据LCD引脚名称创建并绑定 Pin 对象
        Create and bind a Pin object based on the pin name.
        :param pin_name: 要创建绑定的LCD引脚名称
        The name of the pin to create and bind.
        :return: 如果创建并绑定成功，返回 True
        Returns True if the creation and binding is successful.
        :raises ValueError: 如果LCD引脚名称无效，则抛出异常
        Raises ValueError if the pin name is invalid.
        """
        # 检查LCD引脚名称是否被启用
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        # 检查所连接的MCU引脚GPIO值是否可用
        if self.enabled_pins[pin_name] not in self.get_mcu_gpio_pins_list():
            raise ValueError(f"Pin {pin_name} is not connected to a valid GPIO pin.")
        # 绑定引脚到实际的GPIO
        self.bind_mcu_pins[pin_name] = Pin(self.enabled_pins[pin_name], Pin.OUT)
        return True
    
    # 根据LCD引脚名称创建并绑定PWM对象
    def bind_mcu_pwm_pin(self, pin_name, freq=1000, duty_u16=32768):
        """
        根据LCD引脚名称创建并绑定 PWM 对象
        Create and bind a PWM object based on the pin name.
        :param pin_name: 要创建并绑定的LCD引脚名称
        The name of the pin to create and bind.
        :param freq: PWM 频率，默认为 1000Hz
        The frequency of the PWM, default is 1000Hz.
        :param duty_u16: PWM 占空比，默认为 32768 (50%)
        The duty cycle of the PWM, default is 32768 (50%).
        :return: 如果创建并绑定成功，返回 True
        Returns True if the creation and binding is successful.
        :raises ValueError: 如果LCD引脚名称无效，则抛出异常
        Raises ValueError if the pin name is invalid.
        """
        # 检查LCD引脚名称是否被启用
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        # 检查所连接的MCU引脚GPIO值是否可用
        if self.enabled_pins[pin_name] not in self.get_mcu_gpio_pins_list():
            raise ValueError(f"Pin {pin_name} is not connected to a valid GPIO pin.")
        # 绑定PWM引脚到实际的GPIO
        self.bind_mcu_pins[pin_name] = PWM(Pin(self.enabled_pins[pin_name]), freq=freq, duty_u16=duty_u16)
        return True
        
    # 初始化已启用的功能引脚，绑定 GPIO Pin 对象
    def bind_function_pins_by_set(self):
        """
        初始化 LCD1602 实例的功能引脚
        Initialize the function pins of the LCD1602 instance.
        :return: 如果初始化成功，返回 True
        Returns True if the initialization is successful.
        """
        # 检测所有已启用的功能引脚
        for pin_name in self.__default_function_pins__:
            if pin_name in self.enabled_pins: # 确保引脚已启用
                if self.enabled_pins[pin_name] in self.get_mcu_gpio_pins_list():
                    self.bind_mcu_pin(pin_name)  # 绑定引脚到实际的GPIO
        return True

    # 将已启用的LCD数据引脚，绑定到 GPIO Pin 对象
    def bind_data_pins_by_set(self):
        """
        绑定 LCD1602 实例的数据引脚到Pin对象
        Bind the data pins of the LCD1602 instance to Pin objects.
        :return: 如果绑定成功，返回 True
        Returns True if the binding is successful.
        """
        # 检测所有已启用的数据引脚
        for pin_name in self.__default_data_pins__:
            if pin_name in self.enabled_pins: # 确保引脚已启用
                if self.enabled_pins[pin_name] in self.get_mcu_gpio_pins_list():
                    self.bind_mcu_pin(pin_name)  # 绑定引脚到实际的GPIO
        return True

    # 初始化PWM引脚，根据设置判断V0和BLA引脚是否需要PWM控制
    def bind_pwm_pins_by_set(self):
        """
        初始化 LCD1602 实例的 PWM 引脚
        Initialize the PWM pins of the LCD1602 instance.
        :return: 如果初始化成功，返回 True
        Returns True if the initialization is successful.
        """
        # 检查 V0 引脚是否需要 PWM 控制
        if self.v0_pwm["enable"]:
            self.unbind_mcu_pin(self.__default_pins__[2])  # 确保先禁用旧的 PWM 引脚
            self.bind_mcu_pwm_pin(self.__default_pins__[2], freq=self.v0_pwm["freq"], duty_u16=self.v0_pwm["duty_u16"])
        # 检查 BLA 引脚是否需要 PWM 控制
        if self.bla_pwm["enable"]:
            self.unbind_mcu_pin(self.__default_pins__[14])  # 确保先禁用旧的 PWM 引脚
            self.bind_mcu_pwm_pin(self.__default_pins__[14], freq=self.bla_pwm["freq"], duty_u16=self.bla_pwm["duty_u16"])
        return True

    # 根据LCD引脚名称删除绑定的Pin对象
    def unbind_mcu_pin(self, pin_name):
        """
        根据LCD引脚名称删除绑定的 Pin 对象
        Delete the bound Pin object based on the pin name.
        :param pin_name: 要删除的LCD引脚名称
        The name of the pin to delete.
        :return: 如果删除成功，返回 True
        Returns True if the deletion is successful.
        :raises ValueError: 如果LCD引脚名称无效，则抛出异常
        Raises ValueError if the pin name is invalid.
        """
        # 检查LCD引脚名称是否被绑定
        if pin_name in self.bind_mcu_pins:
            del self.bind_mcu_pins[pin_name]
            return True
        else:
            return False

    # 添加MCU的GPIO引脚到可用引脚列表
    def add_mcu_gpio_pin(self, pin_name):
        """
        添加MCU的GPIO引脚到可用引脚列表
        Add an MCU GPIO pin to the available pin list.
        :param pin_name: 要添加的MCU GPIO引脚名称
        The name of the MCU GPIO pin to add.
        """
        # pin_name必须是0或正整数，否则抛出异常
        if not isinstance(pin_name, int) or pin_name < 0 or pin_name > 1024:
            raise ValueError("Invalid pin name. Pin name must be a positive integer(0-1024).")
        if pin_name not in self.mcu_gpio_pin_range:
            self.mcu_gpio_pin_range.append(pin_name)
        return True

    # 删除MCU的GPIO引脚从可用引脚列表
    def remove_mcu_gpio_pin(self, pin_name):
        """
        删除MCU的GPIO引脚从可用引脚列表
        Remove an MCU GPIO pin from the available pin list.
        :param pin_name: 要删除的MCU GPIO引脚名称
        The name of the MCU GPIO pin to remove.
        """
        if pin_name in self.mcu_gpio_pin_range:
            self.mcu_gpio_pin_range.remove(pin_name)
            return True
        else:
            return False

    # ########################################
    # 以下是获取并返回引脚信息以便程序处理的方法
    #

    # 获取所有已启用的LCD引脚的信息
    def get_enabled_pins(self):
        """
        获取 LCD1602 实例所有已启用的引脚信息
        Get all enabled pin information of the LCD1602 instance.
        :return: 包含已启用的LCD引脚名称和连接的字典
        A dictionary containing enabled LCD pin names and their connections.
        """
        return self.enabled_pins.copy()
    
    # 获取按预设顺序排列的已启用的引脚列表
    def get_enabled_pins_list(self):
        """
        获取按预设顺序排列的已启用的引脚列表
        Get a list of enabled pins in the preset order.
        :return: 包含已启用的LCD引脚名称的列表
        A list containing enabled LCD pin names.
        """
        return [pin for pin in self.__default_pins__ if pin in self.enabled_pins]
    
    # 获取已启用的LCD功能引脚信息
    def get_enabled_function_pins(self):
        """
        获取 LCD1602 实例所有已启用的功能引脚信息
        Get all enabled function pin information of the LCD1602 instance.
        :return: 包含已启用的LCD功能引脚名称和连接的字典
        A dictionary containing enabled LCD function pin names and their connections.
        """
        function_pins = self.__default_function_pins__
        return {pin: self.enabled_pins[pin] for pin in function_pins if pin in self.enabled_pins}

    # 获取按预设顺序排列的已启用的功能引脚列表
    def get_enabled_function_pins_list(self):
        """
        获取按预设顺序排列的已启用的功能引脚列表
        Get a list of enabled function pins in the preset order.
        :return: 包含已启用的LCD功能引脚名称的列表
        A list containing enabled LCD function pin names.
        """
        return [pin for pin in self.__default_function_pins__ if pin in self.enabled_pins]

    # 获取已启用的LCD数据引脚信息
    def get_enabled_data_pins(self):
        """
        获取 LCD1602 实例所有已启用的数据引脚信息
        Get all enabled data pin information of the LCD1602 instance.
        :return: 包含已启用的LCD数据引脚名称和连接的字典
        A dictionary containing enabled LCD data pin names and their connections.
        """
        data_pins = self.__default_data_pins__
        return {pin: self.enabled_pins[pin] for pin in data_pins if pin in self.enabled_pins}

    # 获取按预设顺序排列的已启用的数据引脚列表
    def get_enabled_data_pins_list(self):
        """
        获取按预设顺序排列的已启用的数据引脚列表
        Get a list of enabled data pins in the preset order.
        :return: 包含已启用的LCD数据引脚名称的列表
        A list containing enabled LCD data pin names.
        """ 
        return [pin for pin in self.__default_data_pins__ if pin in self.enabled_pins]

    # 获取所有可用的MCU GPIO引脚名称列表
    def get_mcu_gpio_pins_list(self):
        """
        获取所有可用的MCU GPIO引脚名称
        Get all available MCU GPIO pin names.
        :return: 包含已启用的MCU GPIO引脚名称的列表
        A list containing enabled MCU GPIO pin names.
        """
        return self.mcu_gpio_pin_range.copy()

    # 获取已启用LCD引脚对应的 Pin 对象
    def get_bind_mcu_pins(self):
        """
        获取 LCD1602 实例所有已启用引脚对应绑定的 Pin 对象
        Get all enabled pin names and their corresponding bound Pin objects of the LCD1602 instance.
        :return: 包含LCD引脚名称和对应绑定的 Pin 对象的字典
        A dictionary containing LCD pin names and their corresponding bound Pin objects.
        """
        return self.bind_mcu_pins.copy()

    # 获取按预设顺序排列的已绑定的引脚列表
    def get_bind_mcu_pins_list(self):
        """
        获取按预设顺序排列的已绑定的引脚列表
        Get a list of bound pins in the preset order.
        :return: 包含已绑定的LCD引脚名称的列表
        A list containing bound LCD pin names.
        """
        return [pin for pin in self.__default_pins__ if pin in self.bind_mcu_pins]
    
    # 获取按预设顺序排列的已绑定的数据引脚列表
    def get_bind_mcu_data_pins_list(self):
        """
        获取按预设顺序排列的已绑定的数据引脚列表
        Get a list of bound data pins in the preset order.
        :return: 包含已绑定的LCD数据引脚名称的列表
        A list containing bound LCD data pin names.
        """
        return [pin for pin in self.__default_data_pins__ if pin in self.bind_mcu_pins]

    # ########################################
    # 以下是向命令行输出LCD引脚状态信息的方法
    #

    # 按顺序向命令行打印所有预定义的LCD引脚状态信息
    def terminal_print_pins(self):
        """
        打印 LCD1602 实例的所有引脚信息
        Print all pin information of the LCD1602 instance.
        """
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
        # 如果没有启用任何引脚，打印提示信息
        if not any(pin in self.enabled_pins for pin in self.__default_pins__):
            print("No pins enabled.")
        else:
            print("Pins enabled.")
        # 返回 None 以表示函数执行完毕
        return None

    # 按顺序向命令行打印预定义的LCD功能引脚状态信息
    def terminal_print_function_pins(self):
        """
        打印 LCD1602 实例的功能引脚信息
        Print function pin information of the LCD1602 instance.
        """
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
        # 如果没有启用任何功能引脚，打印提示信息
        if not any(pin in self.enabled_pins for pin in function_pins):
            print("No function pins enabled.")
        else:
            print("Function pins enabled.")
        # 返回 None 以表示函数执行完毕
        return None

    # 按顺序向命令行打印预定义的LCD数据引脚状态信息
    def terminal_print_data_pins(self):
        """
        打印 LCD1602 实例的数据引脚信息
        Print data pin information of the LCD1602 instance.
        """
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
        # 如果没有启用任何数据引脚，打印提示信息
        if not any(pin in self.enabled_pins for pin in data_pins):
            print("No data pins enabled.")
        else:
            print("Data pins enabled.")
        # 返回 None 以表示函数执行完毕
        return None

    # ########################################
    # 以下是关于LCD基本控制命令的方法
    #

    # 通过E发送使能脉冲信号
    def pulse_enable(self):
        """
        发送使能脉冲信号
        Send a pulse to the enable pin.
        """
        self.bind_mcu_pins[self.__default_pins__[5]].value(1)
        time.sleep_us(1)
        self.bind_mcu_pins[self.__default_pins__[5]].value(0)
        time.sleep_us(100)

    # 发送清屏命令
    def set_clear(self):
        """
        清屏
        Clear the LCD display.
        """
        self.send_byte_command(self.command["LCD_CLEARDISPLAY"])  # 发送清屏命令
        self.settings["cursor_position"] = 0x00
        time.sleep_ms(2)  # 等待清屏完成
        return True
    # 清屏命令别名
    def clear(self):
        return self.set_clear()

    # 清空指定行
    def clear_line(self, line=0):
        """
        清空指定行
        Clear the specified line.
        """
        self.cursor_position(line, 0)
        for i in range(40):
            self.send_byte_data(0x20)
        self.cursor_position(line, 0)
        return True

    # 发送光标归位命令
    def set_cursor_return_home(self):
        """
        光标归位
        Set the cursor to the home position.
        """
        self.send_byte_command(self.command["LCD_RETURNHOME"])  # 光标归位到左上角00位置
        self.settings["cursor_position"] = 0x00
        time.sleep_ms(2)  # 等待光标归位完成
        return True

    # 设置光标AC的Increase模式
    def set_ac_auto_increase(self, mode=True):
        """
        设置光标AC的Increase模式
        Set the cursor AC increase mode.
        """
        if mode not in [True, False]:
            return False
        else:
            self.settings["ac_auto_increase"] = mode
            self.set_ac_display_mode()  # 更新AC增减和显示跟随模式
            return True

    # 设置显示自动跟随光标移动
    def set_display_follow_cursor(self, mode=False):
        """
        设置显示自动跟随光标移动
        Set the display follow cursor mode.
        """
        if mode not in [True, False]:
            return False
        else:
            self.settings["display_follow_cursor"] = mode
            self.set_ac_display_mode()  # 更新AC增减和显示跟随模式
            return True

    # 总体设置AC增减和显示跟随模式
    def set_ac_display_mode(self):
        """
        设置AC增减和显示跟随模式
        Set the AC increase/decrease and display follow mode.
        """
        # 先将布尔值转为0/1
        ac = int(bool(self.settings["ac_auto_increase"]))
        display = int(bool(self.settings["display_follow_cursor"]))
        # 组合命令表
        cmds = [
            [self.command["LCD_ENTRYMODESET_1"], self.command["LCD_ENTRYMODESET_2"]],
            [self.command["LCD_ENTRYMODESET_3"], self.command["LCD_ENTRYMODESET_4"]],
        ]
        # 选择命令并发送
        self.send_byte_command(cmds[ac][display])
        time.sleep_us(40)  # 等待命令执行完成
        return True

    # 设置显示开关
    def set_display_on(self, mode=True):
        """
        设置显示开关
        Set the display on/off mode.
        """
        if mode not in [True, False]:
            return False
        else:
            self.settings["display_on"] = mode
            self.set_display_cursor_blink_mode()  # 更新显示/光标/闪烁状态
            return True

    # 设置是否显示光标
    def set_cursor_visible(self, mode=True):
        """
        设置是否显示光标
        Set the cursor visibility.
        """
        if mode not in [True, False]:
            return False
        else:
            self.settings["cursor_visible"] = mode
            self.set_display_cursor_blink_mode()  # 更新显示/光标/闪烁状态
            return True

    # 设置光标是否闪烁
    def set_cursor_blink(self, mode=True):
        """
        设置光标是否闪烁
        Set the cursor blink mode.
        """
        if mode not in [True, False]:
            return False
        else:
            self.settings["cursor_blink"] = mode
            self.set_display_cursor_blink_mode()  # 更新显示/光标/闪烁状态
            return True

    # 总体设置显示/光标/闪烁状态
    def set_display_cursor_blink_mode(self):
        """
        设置显示/光标/闪烁状态（通过命令表全覆盖8种组合）
        Set the display/cursor/blink status using command table.
        """
        # 先将布尔值转为0/1
        display = int(bool(self.settings["display_on"]))
        cursor = int(bool(self.settings["cursor_visible"]))
        blink = int(bool(self.settings["cursor_blink"]))
        # 8种组合命令表
        cmds = [
            self.command["LCD_DISPLAYCONTROL_1"], # 0x08: 显示关，光标关，闪烁关
            self.command["LCD_DISPLAYCONTROL_2"], # 0x09: 显示关，光标关，闪烁开
            self.command["LCD_DISPLAYCONTROL_3"], # 0x0A: 显示关，光标开，闪烁关
            self.command["LCD_DISPLAYCONTROL_4"], # 0x0B: 显示关，光标开，闪烁开
            self.command["LCD_DISPLAYCONTROL_5"], # 0x0C: 显示开，光标关，闪烁关
            self.command["LCD_DISPLAYCONTROL_6"], # 0x0D: 显示开，光标关，闪烁开
            self.command["LCD_DISPLAYCONTROL_7"], # 0x0E: 显示开，光标开，闪烁关
            self.command["LCD_DISPLAYCONTROL_8"], # 0x0F: 显示开，光标开，闪烁开
        ]
        idx = (display << 2) | (cursor << 1) | blink
        self.send_byte_command(cmds[idx])
        time.sleep_us(40)  # 等待命令执行完成
        return True

    # 动态设置数据传输模式
    def set_data_trans_bits(self, bits=4):
        """
        设置 LCD1602 实例的数据传输模式
        Set the data transmission mode of the LCD1602 instance.
        :param mode: 数据传输模式，可以是 4 或 8
        The data transmission mode, can be 4 or 8.
        """
        # 检查模式是否有效
        if bits not in [4, 8]:
            raise ValueError("Invalid data transmission mode. Use 4 or 8.")
        # 更新数据传输模式设置
        self.settings["data_trans_bits"] = bits
        self.set_data_lines_matrix_mode()  # 更新数据传输接口/显示行数/字符点阵
        # 更新数据模式后，须重新手动初始化数据引脚，Pin状态才可用
        self.is_pin_ready = False
        self.is_read_ready = False
        self.is_write_ready = False
        return True

    # 设置显示行数
    def set_display_lines(self, lines=2):
        """
        设置显示行数
        Set the display lines.
        """
        if lines not in [1, 2]:
            return False
        else:
            self.settings["display_lines"] = lines
            self.set_data_lines_matrix_mode()  # 更新数据传输接口/显示行数/字符点阵
            return True

    # 设置显示字符点阵大小
    def set_dot_matrix(self, size=7):
        """
        设置显示字符点阵大小
        Set the display character dot matrix size.
        """
        if size not in [7, 10]:
            return False
        else:
            self.settings["dot_matrix"] = size
            self.set_data_lines_matrix_mode()  # 更新数据传输接口/显示行数/字符点阵
            return True

    # 总体设置数据传输接口/显示行数/字符点阵
    def set_data_lines_matrix_mode(self):
        """
        设置数据传输接口/显示行数/字符点阵
        Set the data transmission interface/display lines/character dot matrix.
        """
        # 根据设置发送相应的命令
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
        time.sleep_us(40)  # 等待命令执行完成
        return True

    # ########################################
    # 以下是关于LCD数据传输的基本显示的方法
    #

    # 按位数选择进行数据发送
    def send_bits(self, value, bits_count=4):
        """
        按位数选择进行数据发送
        Send data according to the bit count.
        """
        # 检查数据是否完成初始化
        if not self.is_pin_ready:
            raise ValueError("Pin is not ready. Please initialize the pin first.")
        data_pins_list = self.get_bind_mcu_data_pins_list()
        if bits_count != len(data_pins_list):
            raise ValueError("Invalid bits count. Please check the data pins configuration.")
        # 通过RW选择进行写操作
        self.bind_mcu_pins[self.__default_pins__[4]].value(0)
        # 发送数据
        for i in range(bits_count):
            self.bind_mcu_pins[data_pins_list[i]].value((value >> i) & 1)
        self.pulse_enable()  # 发送使能脉冲信号
        return True

    # 发送字节
    def send_byte(self, value):
        """
        发送字节
        Send a byte.
        """
        if not isinstance(value, int):
            raise ValueError("Invalid value type. Expected an integer.")
        # 根据数据传输模式设置发送位数
        if self.settings["data_trans_bits"] == 4:
            self.send_bits(value >> 4, 4) #发送高4位数据
            self.send_bits(value & 0x0F, 4) #发送低4位数据
        elif self.settings["data_trans_bits"] == 8:
            self.send_bits(value, 8)
        else:
            raise ValueError("Invalid data transmission mode. Use '4bits' or '8bits'.")
        return True

    # 发送LCD字节命令
    def send_byte_command(self, value):
        """
        发送命令
        Send a command.
        """
        # 通过RS选择发送命令还是发送数据
        self.bind_mcu_pins[self.__default_pins__[3]].value(0)
        self.send_byte(value)  # 发送命令
        return True

    # 发送LCD字节数据
    def send_byte_data(self, value):
        """
        发送数据
        Send a byte.
        """
        # 通过RS选择发送命令还是发送数据
        self.bind_mcu_pins[self.__default_pins__[3]].value(1)
        self.send_byte(value)  # 发送数据
        # 更新光标指示器
        self.cursor_position_increase()
        return True

    # 向屏幕发送单个字符
    def print_char(self, char):
        """
        打印单个字符
        Print a single character.
        """
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("Invalid character. Expected a single character string.")
        self.send_byte_data(ord(char))
        return True

    # 向LCD缓冲区第0行或第1行写入数据，每行最大写入40字节，超出16字节部分默认将不显示
    def print_line(self, text, line=0):
        """ 按行发送比显示字符串到LCD
        Print a string to the LCD line by line.
        :param text: 要发送的字符串
        The string to send.
        :return: 如果发送成功，返回 True
        Returns True if the sending is successful.
        """
        if line not in [0, 1]:
            raise ValueError("Invalid line number. Line must be 0 or 1.")
        # 检查数据是否完成初始化
        if not self.is_write_ready:
            raise ValueError("Write is not ready. Please initialize the write first.")
        # 打印前先清除行
        self.clear_line(line)
        # 将字符串转换为ASCII码
        for char in text[:40]:
            self.send_byte_data(ord(char))
        return True

    # 以翻页方式逐页显示长文本
    def print(self, text, speed=1, line_width=16):
        """
        以翻页方式逐页显示长文本
        Print long text page by page.
        """
        if line_width < 1 or line_width > 40:
            line_width = 16
        # 将长文本分割为多页
        pages = [text[i:i + line_width] for i in range(0, len(text), line_width)]
        interval = 1 / speed
        pages_lens = len(pages)
        for lp in range(pages_lens):
            if lp + 1 < pages_lens:
                self.print_line(pages[lp], 0)
                self.print_line(pages[lp + 1], 1)
            else:
                self.print_line(pages[lp], 0)
                self.clear_line(1)  # 最后一页只显示一行
            time.sleep(interval)
        self.set_clear()
        return True

    # 在屏幕第0行或第1行滚屏显示字符串1次
    def scroll_line(self, text, line=0, speed=3):
        """
        在指定行滚动显示字符串
        Scroll a string on the specified line.
        Params:
        text: The text to scroll.
        line: The line number to display the text on (0 or 1).
        speed: The speed of the scrolling (default is 2).
        """
        # 检查数据是否完成初始化
        if not self.is_write_ready:
            raise ValueError("Write is not ready. Please initialize the write first.")
        # 隐藏光标
        # self.send_byte_command(self.command["LCD_DISPLAYCONTROL_5"])
        # 重置光标到指定行首
        self.cursor_position(line, 0)
        paded_text = " " * 16 + text + " " * 16
        interval = 1 / speed
        for i in range(len(paded_text) - 16):
            text_slice = paded_text[i:i + 16]
            self.print_line(text_slice, line)
            time.sleep(interval)
        # 清除该行内容
        self.clear_line(line)
        return True

    # ########################################
    # 以下是关于光标显示和状态控制的方法
    #

    # 开启显示
    def display_on(self):
        """
        开启显示
        Turn on the display.
        """
        return self.set_display_on(True)  # 设置显示开
    
    # 关闭显示
    def display_off(self):
        """
        关闭显示
        Turn off the display.
        """
        return self.set_display_on(False)  # 设置显示关

    # 隐藏闪烁和光标
    def hide_blink_cursor(self):
        """
        隐藏闪烁和光标
        Hide the blinking and the cursor.
        """
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_5"]) 
        return True

    # 显示闪烁
    def show_blink(self):
        """
        显示闪烁
        Show the blinking.
        """
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_6"])  # 闪烁
        return True

    # 显示静态光标
    def show_cursor(self):
        """
        显示光标
        Show the cursor.
        """
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_7"])  # 光标
        return True

    # 显示闪烁光标
    def show_blink_cursor(self):
        """
        显示闪烁光标
        Show the blinking cursor.
        """
        self.send_byte_command(self.command["LCD_DISPLAYCONTROL_8"])  # 光标闪烁
        return True

    # 设置光标归位
    def cursor_home(self):
        """
        设置光标归位
        Set the cursor to the home position.
        """
        return self.set_cursor_return_home()  # 光标归位到左上角00位置

    # 设置光标位置
    def cursor_position(self, row, column):
        """
        设置光标位置
        Set the cursor position.
        """
        if not (0 <= row < 2):
            raise ValueError("Invalid row position. Row must be 0 or 1.")
        if not (0 <= column < 40):
            raise ValueError("Invalid column position. Column must be between 0 and 39.")
        self.settings["cursor_position"] = (row * 0x40) + column
        self.send_byte_command(self.command["LCD_SETDDRAMADDR"] | self.settings["cursor_position"])
        return True

    # 光标位置指示器左移
    def cursor_position_decrease(self):
        """
        光标位置指示器左移1格
        Move the cursor position indicator to the left by 1 position.
        """
        # 更新光标位置
        if self.settings["cursor_position"] < 0x28:
            self.settings["cursor_position"] -= 1
        elif self.settings["cursor_position"] == 0x00:
            self.settings["cursor_position"] = 0x67
        elif self.settings["cursor_position"] < 0x68:
            self.settings["cursor_position"] -= 1
        elif self.settings["cursor_position"] == 0x40:
            self.settings["cursor_position"] = 0x27
        return True

    # 光标位置指示器右移
    def cursor_position_increase(self):
        """
        光标位置指示器右移1格
        Move the cursor position indicator to the right by 1 position.
        """
        # 更新光标位置
        if self.settings["cursor_position"] < 0x27:
            self.settings["cursor_position"] += 1
        elif self.settings["cursor_position"] == 0x27:
            self.settings["cursor_position"] = 0x40
        elif self.settings["cursor_position"] < 0x67:
            self.settings["cursor_position"] += 1
        elif self.settings["cursor_position"] == 0x67:
            self.settings["cursor_position"] = 0x00
        return True

    # 光标往左移动
    def cursor_move_left(self):
        """
        光标往左移动1格
        Move the cursor to the left.
        """
        if self.settings["cursor_position"] & 0x3F > 0:
            self.settings["cursor_position"] -= 1
            self.send_byte_command(self.command["LCD_CURSORSHIFT_1"])  # 光标左移
        elif self.settings["cursor_position"] & 0x3F == 0:
            self.settings["cursor_position"] = self.settings["cursor_position"] + 0x27  # 光标左移循环跳到末列
            self.cursor_position((self.settings["cursor_position"] & 0x40) >> 6, 0x27)
        return True

    # 光标往右移动
    def cursor_move_right(self):
        """
        光标往右移动1格
        Move the cursor to the right.
        """
        if self.settings["cursor_position"] & 0x3F < 0x27:
            self.settings["cursor_position"] += 1
            self.send_byte_command(self.command["LCD_CURSORSHIFT_2"])  # 光标右移
        elif self.settings["cursor_position"] & 0x3F == 0x27:
            self.settings["cursor_position"] = self.settings["cursor_position"] - 0x27  # 光标左右循环跳到首列
            self.cursor_position((self.settings["cursor_position"] & 0x40) >> 6, 0x00)
        return True

    # 光标往上移动
    def cursor_move_up(self):
        """
        光标往上移动1格
        Move the cursor to the up.
        """
        if self.settings["cursor_position"] >= 0x40:
            self.settings["cursor_position"] -= 0x40
            self.send_byte_command(self.command["LCD_SETDDRAMADDR"] | self.settings["cursor_position"])  # 光标上移
        return True

    # 光标往下移动
    def cursor_move_down(self):
        """
        光标往下移动1格
        Move the cursor to the down.
        """
        if self.settings["cursor_position"] < 40:
            self.settings["cursor_position"] += 0x40
            self.send_byte_command(self.command["LCD_SETDDRAMADDR"] | self.settings["cursor_position"])  # 光标下移
        return True

    # ########################################
    # 以下是关于 Text Browser 模块的处理的方法
    #

    # 设置Browser缓冲区大小
    def browser_set_content_max_length(self, content_max_length=1024):
        """
        设置Browser缓冲区大小
        Set the size of the browser buffer.
        :param content_max_length: 缓冲区最大内容长度
        """
        self.browser["content_max_length"] = content_max_length
        return True
    # 设置Browser缓冲区大小的别名
    def browser_set_buffer_size(self, content_max_length=1024):
        return self.browser_set_content_max_length(content_max_length)

    # 获取Browser缓冲区大小
    def browser_get_content_max_length(self):
        """
        获取Browser缓冲区大小
        Get the size of the browser buffer.
        :return: 缓冲区最大内容长度
        """
        return self.browser["content_max_length"]
    # 获取Browser缓冲区大小的别名
    def browser_get_buffer_size(self):
        return self.browser_get_content_max_length()

    # 获取Browser所有内容
    def browser_get_content(self):
        """
        获取Browser所有内容
        Get all content from the browser.
        :return: 所有内容
        """
        return self.browser["content"]

    # 获取Browser内容长度
    def browser_get_content_length(self):
        """
        获取Browser内容长度
        Get the content length of the browser.
        :return: 内容长度
        """
        return self.browser["content_length"]

    # 设置Browser行宽
    def browser_set_line_width(self, line_width=16):
        """
        设置Browser行宽
        Set the line width of the browser.
        :param line_width: 行宽
        """
        if line_width < 1 or line_width > 40:
            return False
        self.browser["line_width"] = line_width
        # 更新行数
        self.browser["line_count"] = (self.browser["content_length"] + line_width - 1) // line_width
        # 初始化行指针
        self.browser["line_pointer"] = 0
        return True

    # 获取Browser行宽
    def browser_get_line_width(self):
        """
        获取Browser行宽
        Get the line width of the browser.
        :return: 行宽
        """
        return self.browser["line_width"]

    # 获取Browser行数
    def browser_get_line_count(self):
        """
        获取Browser行数
        Get the line count of the browser.
        :return: 行数
        """
        return self.browser["line_count"]

    # 设置Browser行指针
    def browser_set_line_pointer(self, line_pointer=0):
        """
        设置Browser行指针
        Set the line pointer of the browser.
        :param line_pointer: 行指针
        """
        if line_pointer < 0:
            line_pointer = 0
        elif line_pointer >= self.browser["line_count"]:
            line_pointer = self.browser["line_count"] - 1
        self.browser["line_pointer"] = line_pointer
        return True

    # 获取Browser行指针
    def browser_get_line_pointer(self):
        """
        获取Browser行指针
        Get the line pointer of the browser.
        :return: 行指针
        """
        return self.browser["line_pointer"]

    # 设置Browser打印速度
    def browser_set_print_speed(self, print_speed=3):
        """
        设置Browser打印速度
        Set the print speed of the browser.
        :param print_speed: 打印速度
        """
        self.browser["print_speed"] = print_speed
        return True

    # 打开Browser内容，并从第1行开始显示
    def browser_open(self):
        """
        打开Browser内容，并从第1行开始显示
        Open the browser content and display from the first line.
        """
        if self.browser["content_length"] == 0:
            self.print("Browser is Empty", 0.33)
            return False
        else:
            self.browser_set_line_pointer(0)
            self.browser_print_2lines()
            return True

    # 清空Browser内容
    def browser_clear(self):
        """
        清空Browser内容
        Clear the browser content.
        """
        self.browser["content"] = ""
        self.browser["content_length"] = 0
        self.browser["line_count"] = 0
        self.browser["line_pointer"] = 0
        return True

    # 返回指定行的内容，不考虑内容格式只按存储字符长度划分行
    def browser_get_1line(self, line_pointer=None):
        """
        从浏览器缓冲区获取指定行的文本内容
        Get the text content of the specified line from the browser buffer.
        :param line: 行号

        :return: 指定行的文本内容
        Returns the text content of the specified line.
        """
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        if 0 <= line_pointer <= self.browser["line_count"] - 1:
            # 获取当前行的内容
            start = line_pointer * self.browser["line_width"]
            end = start + self.browser["line_width"]
            return self.browser["content"][start:end] if start < self.browser["content_length"] else ""
        else:
            return ""

    # 打印行指针内容到屏幕指定行
    def browser_print_1line(self, line_pointer=None, line=0):
        """
        打印浏览器行指针所在的1行或指定的1行
        Print the line where the browser line pointer is located.
        :param line_pointer: 行指针
        """
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        content = self.browser_get_1line(line_pointer)
        self.print_line(content, line)
        return True

    # 根据行指针打印2行内容
    def browser_print_2lines(self, line_pointer=None):
        """
        打印浏览器行指针所在的2行或指定的2行
        Print the two lines where the browser line pointer is located.
        """
        if line_pointer is None:
            line_pointer = self.browser["line_pointer"]
        content0 = self.browser_get_1line(line_pointer)
        content1 = self.browser_get_1line(line_pointer + 1)
        self.print_line(content0, 0)
        self.print_line(content1, 1)
        return True

    # 向上移动行指针并打印2行内容
    def browser_line_up(self):
        """
        向上移动行指针1行并打印2行内容
        Move the line pointer up 1 line and print 2 lines.
        """
        self.browser_set_line_pointer(self.browser_get_line_pointer() - 1)
        self.browser_print_2lines()
        return True

    # 向下移动行指针并打印2行内容
    def browser_line_down(self):
        """
        向下移动行指针1行并打印2行内容
        Move the line pointer down 1 line and print 2 lines.
        """
        self.browser_set_line_pointer(self.browser_get_line_pointer() + 1)
        self.browser_print_2lines()
        return True

    # 向上移动行指针并打印2行内容
    def browser_page_up(self):
        """
        向上移动行指针2行并打印2行内容
        Move the line pointer up 2 lines and print 2 lines.
        """
        self.browser_set_line_pointer(self.browser_get_line_pointer() - 2)
        self.browser_print_2lines()
        return True

    # 向下移动行指针并打印2行内容
    def browser_page_down(self):
        """
        向下移动行指针2行并打印2行内容
        Move the line pointer down 2 lines and print 2 lines.
        """
        self.browser_set_line_pointer(self.browser_get_line_pointer() + 2)
        self.browser_print_2lines()
        return True

    # 在LCD指定行滚屏轮播显示多行内容
    def browser_scroll_1lines(self, line_pointer=None, count=1, line=0, speed=None):
        """
        在LCD指定1行滚屏轮播显示多行内容
        Scroll and display multiple lines on the specified line of the LCD.
        :param line_pointer: 行指针
        :param count: 从行指针开始计算的滚动行数
        :param line: 选择显示行号 0 或 1
        :param speed: 滚动速度
        """
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

    # 在LCD的2行滚屏轮播显示多行内容
    def browser_scroll_2lines(self, line_pointer=None, count=1, speed=None):
        """
        在LCD的2行滚屏轮播显示多行内容
        Scroll and display multiple lines on the 2 lines of the LCD.
        :param line_pointer: 行指针
        :param count: 从行指针开始计算的滚动行数
        :param speed: 滚动速度
        """
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
                self.clear_line(1)  # 最后一行只显示一行
            time.sleep(interval)
        self.set_clear()
        return True

    # 向浏览器缓冲区追加写入内容并显示到LCD
    def browser_write(self, text):
        """
        打印浏览器缓冲区的内容
        Print the content of the browser buffer.
        """
        # 计算内容长度
        text_length = len(text)
        if text_length > self.browser["content_max_length"]:
            raise ValueError("Content length exceeds maximum limit.")
        # 如果当前内容长度加上新内容长度超过最大限制，则删除最早的内容
        if self.browser["content_length"] + text_length > self.browser["content_max_length"]:
            del_length = (self.browser["content_length"] + text_length) - self.browser["content_max_length"]
            self.browser["content"] = self.browser["content"][del_length:]
        # 追加新内容
        self.browser["content"] += text
        self.browser["content_length"] = len(self.browser["content"])
        self.browser["line_count"] = (self.browser["content_length"] + self.browser["line_width"] - 1) // self.browser["line_width"]
        self.browser["line_pointer"] = self.browser["line_count"] - 1  # 更新行指针到最后一行
        # 滚动显示新内容
        text_line_count = (text_length + self.browser["line_width"] - 1) // self.browser["line_width"]
        self.browser_scroll_2lines(self.browser["line_pointer"] - text_line_count + 1, text_line_count, self.browser["print_speed"])
        return True
    # browser_write的别名
    def browser_print(self, text):
        return self.browser_write(text)

    # ########################################
    # 以下是一些Widget​小工具方法
    #
    
    # 根据百分比生成PWM占空比
    def percent_to_pwm_duty_u16(self, percent):
        """
        将百分比转换为 PWM 占空比
        Convert percentage to PWM duty cycle.
        :param percent: 百分比值，范围为 0-100
        The percentage value, range from 0 to 100.
        :return: 对应的 PWM 占空比值
        Returns the corresponding PWM duty cycle value.
        """
        if not (0 <= percent <= 100):
            raise ValueError("Percent must be between 0 and 100.")
        return int(percent * 65535 / 100)

    # 设置显示对比度
    def display_contrast(self, percent):
        """
        设置 LCD1602 显示对比度
        Set the contrast of the LCD1602 display.
        :param percent: 对比度百分比，范围为 0-100
        The contrast percentage, range from 0 to 100.
        """
        # 检查是否启用 V0 PWM 控制
        if not self.v0_pwm["enable"]:
            raise ValueError("V0 PWM control is not enabled. Please enable it first.")
        pin_name = self.v0_pwm["pin_name"]
        # 检查引脚是否已启用
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        # 检查引脚是否已经绑定到实际的 Pin 对象
        if pin_name not in self.bind_mcu_pins:
            raise ValueError(f"Pin {pin_name} is not initialized. Please bind it first.")
        # 检查引脚是否为 PWM 引脚
        if not isinstance(self.bind_mcu_pins[pin_name], PWM):
            raise ValueError(f"Pin {pin_name} is not a PWM pin.")
        # 检查百分比范围
        if not (0 <= percent <= 100):
            raise ValueError("Contrast percent must be between 0 and 100.")

        # 计算占空比
        duty = self.percent_to_pwm_duty_u16(percent)
        # 更新 PWM 设置
        self.v0_pwm["duty_u16"] = duty
        self.v0_pwm["contrast_percent"] = percent
        # 刷新 PWM 引脚的占空比
        self.bind_mcu_pins[pin_name].duty_u16(duty) # 设置 PWM 占空比
        return True

    # 设置背光亮度
    def backlight_brightness(self, percent):
        """
        设置 LCD1602 背光亮度
        Set the backlight brightness of the LCD1602.
        :param percent: 背光亮度百分比，范围为 0-100
        The backlight brightness percentage, range from 0 to 100.
        """
        # 检查是否启用 BLA PWM 控制
        if not self.bla_pwm["enable"]:
            raise ValueError("BLA PWM control is not enabled. Please enable it first.")
        pin_name = self.bla_pwm["pin_name"]
        # 检查引脚是否已启用
        if pin_name not in self.enabled_pins:
            raise ValueError(f"Pin {pin_name} is not enabled. Please enable it first.")
        # 检查引脚是否已绑定
        if pin_name not in self.bind_mcu_pins:
            raise ValueError(f"Pin {pin_name} is not initialized. Please bind it first.")
        # 检查引脚是否为 PWM 引脚
        if not isinstance(self.bind_mcu_pins[pin_name], PWM):
            raise ValueError(f"Pin {pin_name} is not a PWM pin.")
        # 检查百分比范围
        if not (0 <= percent <= 100):
            raise ValueError("Backlight brightness percent must be between 0 and 100.")

        # 计算占空比
        duty = self.percent_to_pwm_duty_u16(percent)
        # 更新 PWM 设置
        self.bla_pwm["duty_u16"] = duty
        self.bla_pwm["brightness_percent"] = percent
        # 刷新 PWM 引脚的占空比
        self.bind_mcu_pins[pin_name].duty_u16(duty)
        return True

    # ########################################
    # 以下是关于功能整体初始化的方法
    #

    # 初始化LED写模式
    def init_lcd_write(self):
        """
        初始化LED写模式
        Initialize the LED write mode.
        """
        # LCD写入模式启动流程
        time.sleep_ms(15) # 上电延时（≥15ms）
        self.set_data_lines_matrix_mode() # 第一次唤醒（试探） 之后等待≥4.1ms
        time.sleep_ms(5)
        self.set_data_lines_matrix_mode() # 第二次唤醒（确认状态） 之后等待≥100μs
        time.sleep_us(100)
        self.set_data_lines_matrix_mode() # 第三次唤醒（强制模式） 之后等待≥40μs
        time.sleep_us(40)
        self.set_data_lines_matrix_mode() # 默认：4bits数据传输，2行显示，5x7字符点阵
        self.set_clear() # 清屏（含延时2ms）
        self.set_cursor_return_home() # 光标归位（含延时2ms）
        self.set_ac_display_mode() # 默认：光标自动右移，屏幕不移
        self.set_display_cursor_blink_mode() # 默认：开显示，开光标，开闪烁
        self.is_write_ready = True
        return True

    # 按默认设置初始化引脚
    def init_default_pins(self):
        """
        按默认设置初始化 LCD1602 实例的引脚
        Initialize the pins of the LCD1602 instance according to the default settings.
        :return: 如果初始化成功，返回 True
        Returns True if the initialization is successful.
        """
        self.is_pin_ready = False
        # 初始化功能引脚
        self.enable_function_pins_by_default()
        self.bind_function_pins_by_set()
        # 初始化数据引脚
        self.enable_data_pins_by_default()
        self.bind_data_pins_by_set()
        # 初始化PWM引脚
        self.bind_pwm_pins_by_set()
        self.is_pin_ready = True
        return True

    # 初始化引脚
    def init_pins(self):
        """
        初始化 LCD1602 实例的引脚
        Initialize the pins of the LCD1602 instance.
        :return: 如果初始化成功，返回 True
        Returns True if the initialization is successful.
        """
        self.is_pin_ready = False
        # 绑定功能引脚
        self.bind_function_pins_by_set()
        # 绑定数据引脚
        self.bind_data_pins_by_set()
        # 绑定PWM引脚
        self.bind_pwm_pins_by_set()
        self.is_pin_ready = True
        return True

    # 按默认配置初始化并启动LCD1602
    def init_by_default(self):
        """
        初始化 LCD1602 实例
        Initialize the LCD1602 instance.
        :return: 如果初始化成功，返回 True
        Returns True if the initialization is successful.
        """
        # 初始化默认引脚
        self.init_default_pins()
        # 初始化LCD可写
        self.init_lcd_write()

        # 这里可以添加更多初始化代码
        return True

    # 手动初始化并启动LCD1602
    def init(self):
        """
        初始化 LCD1602 实例
        Initialize the LCD1602 instance.
        :return: 如果初始化成功，返回 True
        Returns True if the initialization is successful.
        """
        # 初始化默认引脚
        self.init_pins()
        # 初始化LCD可写
        self.init_lcd_write()

        # 这里可以添加更多初始化代码
        return True
