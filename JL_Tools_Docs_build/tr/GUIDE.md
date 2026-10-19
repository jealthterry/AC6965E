# Translation guide — Jieli Tools documentation (Chinese → English)

You are translating the official documentation of Zhuhai Jieli Technology (杰理科技), a maker of Bluetooth
audio SoCs, for its development, firmware and mass-production tools: toolchain and IDE setup, firmware
editing and upgrade tools, 1-to-2 / 1-to-8 production programmers, a Bluetooth test box, licensing tools.
Readers are embedded engineers and factory/production staff who do not read Chinese. They will use the
English text next to screenshots that remain in Chinese.

## Input / output

* Input: `tr/batches/bNN.json` → `pages[] → units[]`. Each unit has `id`, `role`, `zh` and sometimes `ctx`.
  Units are in document order, grouped by page (`page`, `page_title`), so read neighbouring units for context.
* Output: `tr/out/bNN.json` — one flat JSON object `{ "<id>": "<English>", ... }` with **every** id of the batch.
  Write valid UTF-8 JSON (escape `"` as `\"` and `\` as `\\`; e.g. `C:\JL\pi32` becomes `"C:\\JL\\pi32"`).
* Then run `python tr/check.py bNN` and fix every ERROR. Read the WARN lines and fix the ones that are real problems.
* Translate everything yourself. Do not use scripts, machine translation services or web lookups to produce the text.

## Placeholders (critical)

Inline markup is replaced by numbered markers: `⟦3⟧ … ⟦/3⟧` (paired: link, bold, inline code, coloured text …)
and `⟦4/⟧` (single: line break or inline image).

* Every marker in `zh` must appear **exactly once** in your English, correctly nested. Never invent new numbers.
* You may move markers to fit English word order. Translate the text inside paired markers (it is link text,
  bold text, etc.), except inline code: if the text inside a marker is code/ASCII (a file name, macro, command,
  value), copy it unchanged.
* `⟦n/⟧` that is a line break: keep it where the line break belongs in the English sentence structure.

## Roles

* `h1`–`h6`: headings. Use sentence case ("Deploy the target chip firmware to the programmer"), no final period,
  **never put Chinese in headings** (headings also appear in the navigation menu).
* `cell`: table cell — keep it concise; keep the same list numbering/line breaks.
* `caption`: figure caption — short noun phrase in sentence case.
* `li`, `p`, `dd`, `dt`, `blockquote`, …: normal prose.
* `code`: text from a code block (`ctx` shows the whole code line when available). Translate **only** Chinese
  comments and human-readable Chinese text. Everything else must stay byte-for-byte identical: code, keys,
  values, symbols, comment markers (`//`, `#`, `;`, `/* */`), spacing, indentation and line breaks. Lines that
  contain no Chinese must not change at all. Chinese that is a real file name (e.g. `固件升级程序_1.4.18.exe`)
  stays as it is. Chinese display strings inside config values (e.g. a button caption `text = 升级`) may be
  translated (`text = Upgrade`).
* `attr`: image alt/title text.

## Style

* Faithful and complete: translate every statement, warning, number and condition. Do not summarise, do not
  drop sentences, do not add your own explanations. If the Chinese is redundant, a slightly tighter English
  sentence is fine, but no information may be lost.
* Clear, natural technical English (US spelling). Use the imperative for steps ("Click …", "Set …").
* Keep unchanged: code, commands, file names, paths, extensions, config keys and values, macros, function and
  register names, URLs, version numbers, chip models (AC696N, AD14, JL7016…), part numbers, units, numbers,
  error codes, and any English already in the text. Keep `FLASH`, `KEY`, `FW`, `UFW`, `SDK`, `LVD`, `MES`,
  `TWS`, `OTA`, `DUT`, `CRC` as written.
* Punctuation: convert full-width punctuation to English punctuation (`，。：；（）！？` → `, . : ; ( ) ! ?`),
  `、` → comma. `【1】` style step markers → `[1]`. Document references in `《…》` → double quotes `"…"`.
  `“…”` quotes → `"…"`.
* **On-screen labels**: when the text names a specific label that appears in a tool, on the programmer's
  display or on the device — a button, menu, tab, option, checkbox, field, dialog title, status or error
  message — translate it and add the original Chinese in parentheses right after it, so readers can find it in
  the Chinese screenshot or software. Example: `勾选“对耳测试使能”` → `Check "TWS pair test enable" (对耳测试使能)`.
  Example: `显示屏显示“空片”` → `the display shows "Blank" (空片)`. Do this only for literal on-screen text, not
  for general concepts, and never in headings. Apart from this and real Chinese file names, the English must
  contain no Chinese characters.
* If the software's interface is actually in English (Code::Blocks, VSCode, English Windows dialogs, or when
  the Chinese text itself quotes an English label), use the real English label and do not add Chinese.
  Add the Chinese in parentheses only for labels that really are Chinese on screen (Jieli tools, programmer
  display, Chinese dialogs). `【编译】`-style labels become `[Build]`.
* Numbered table-of-contents entries such as `1.2.1. 烧录环境准备` are links to section headings: translate them
  like headings (sentence case; page-level entries use the fixed page titles below). The site generator will
  align them with the final headings automatically, so do not worry about matching other batches exactly.
* `小机` (the target board running the firmware) → "target device".
* `杰理` / `杰理科技` → Jieli / Jieli Technology. `点击此处下载` → "click here to download".
  `联系杰理技术支持` / `联系杰理FAE` → "contact Jieli technical support" / "contact a Jieli FAE".

## Glossary (use these consistently)

| Chinese | English |
|---|---|
| 烧录 / 烧写 | program / programming (writing firmware into a chip) |
| 烧录器 / 烧写器 | programmer |
| 一拖二 / 一拖八 / 一拖一 | 1-to-2 / 1-to-8 / 1-to-1 |
| 烧录文件 | programming file |
| 烧录次数 | programming count |
| 烧录座 / socket座 / socket板 | programming socket / socket / socket board |
| 上层板 | top board |
| 转接板 | adapter board |
| 裸片 | bare chip |
| 样机 | device (the assembled board/product being programmed or tested) |
| 样机带电池 | device with battery attached |
| 目标芯片程序 | target chip firmware |
| 部署 | deploy |
| 机台 / 机台自动烧录 | handler (automatic programming machine) / automated programming with a handler |
| 校验 | verify / verification |
| 查空 / 空片 | blank check / blank chip |
| 擦除 / 全片擦除 | erase / full-chip erase |
| 校验码 | checksum |
| 固件 | firmware |
| 程序 | program / firmware (whichever fits; 芯片程序 = chip firmware) |
| 升级 / 更新 | upgrade / update |
| 远程升级 | remote upgrade |
| 强制升级工具 | Forced Upgrade Tool |
| 下载 (to a chip) | download |
| 下载目录 | download directory |
| 工具链 | toolchain |
| 工程 | project |
| 编译 / 链接 | build (compile) / link |
| 编译参数 / 链接参数 | compiler flags / linker flags |
| 宏定义 | macro definition |
| 上位机 / PC端 / PC工具 | PC tool |
| 控制界面 | control panel (of the PC tool) |
| 测试盒 | test box |
| 治具 | fixture |
| 量产 / 产测 | mass production / production test |
| 测试项 / 用例 | test item / test case |
| 授权 | authorization (authorize, authorized) |
| 授权数据 / 授权次数 | authorization data / authorized count |
| 多算法授权 | multi-algorithm authorization |
| 授权执行文件 | authorization executable |
| 算法提供商 / 生产商 | algorithm provider / manufacturer |
| 私有数据授权 | private data authorization |
| 机器码 | machine code |
| 认证码 | authentication code |
| 第三方数据 | third-party data |
| 秘钥 / 密钥 | key |
| 写保护 / 保护参数 | write protection / protection parameters |
| 专家选项 / 烧录选项 | expert options / programming options |
| 配置项 | configuration item / option |
| 勾选 / 取消勾选 | check / uncheck |
| 串口 | serial port (UART) |
| 单线 / 双线串口 | single-wire / two-wire UART |
| 虚拟串口 | virtual serial port |
| 波特率 | baud rate |
| 拨码开关 | DIP switch |
| 钮子开关 | toggle switch |
| 指示灯 | indicator light |
| 显示屏 / 液晶显示屏 | display / LCD display |
| 蜂鸣器 | buzzer |
| 按键 / 开始按键 | button / Start button |
| 复位 | reset |
| 上电 / 断电 / 重新上电 | power on / power off / power-cycle |
| 供电 | power supply (supply power to) |
| 通道 | channel |
| 换板时间 | board-change interval |
| 电流 / 功耗 | current / power consumption |
| 频偏 / 频偏校准 / 频偏测试 | frequency offset / frequency offset calibration / frequency offset test |
| 校频波 / 频点 | calibration signal / frequency point |
| 内置 flash / 外挂 flash | internal flash / external flash |
| 预留区域 | reserved area |
| 提示音 | prompt tone |
| 蓝牙名 / 蓝牙地址 | Bluetooth name / Bluetooth address |
| 自增 | auto-increment |
| 对耳 | earbud pair (TWS pair) |
| 入耳检测 | in-ear detection |
| 仓储模式 | storage mode |
| 透传 | passthrough |
| 免晶振 | crystal-less |
| 芯片型号 | chip model |
| 硬件版本 / 固件版本 | hardware version / firmware version |
| 正式版本 | official release |
| 进度条 | progress bar |
| 技术支持 | technical support |
| 杰理服务器 | Jieli server |
| 报错 / 报错提示 | error / error message |
| 异常 | abnormal / error (context) |

## Page titles (fixed — use these names when the text refers to a page)

| Chinese page title | English |
|---|---|
| 欢迎使用杰理工具文档 | Welcome to the Jieli Tools Documentation |
| 开发环境安装说明 | Development Environment Installation |
| 安装 Code::Blocks | Installing Code::Blocks |
| 安装杰理工具链 | Installing the Jieli Toolchain |
| 更新杰理工具链 | Updating the Jieli Toolchain |
| SDK 编译以及下载 | Building and Downloading the SDK |
| 使用 Code::Blocks 进行编译 | Building with Code::Blocks |
| 使用 make 进行编译 | Building with make |
| 使用 VSCode 进行编译 | Building with VSCode |
| 应该如何实现某功能 | How-To Guides |
| 添加新的文件到工程中编译 | Adding New Files to a Project |
| 如何查看当前工程是什么工具 | How to Check Which Toolset the Current Project Uses |
| 如何添加编译参数 | How to Add Compiler Flags |
| 如何添加宏定义 | How to Add Macro Definitions |
| 如何添加搜索路径（-I..） | How to Add Include Search Paths (-I..) |
| 如何设置链接参数 | How to Set Linker Flags |
| 如何添加编译后执行脚本 | How to Add a Post-Build Script |
| 如何添加编译前执行脚本 | How to Add a Pre-Build Script |
| 如何新建编译库的工程 | How to Create a Library Project |
| 如何新建编译可执行程序工程 | How to Create an Executable Project |
| 如何设置当前工程的输出文件路径 | How to Set the Output File Path of the Current Project |
| 常见报错 | Common Errors |
| Environment error（找不到GNU GCC） | Environment Error (GNU GCC Not Found) |
| 打开工程提示不能找到编译器配置（cannot find/run the compiler） | "Cannot Find Compiler Configuration" When Opening a Project (cannot find/run the compiler) |
| 不支持的16位应用程序/已停止工作 | "Unsupported 16-Bit Application" / "Has Stopped Working" |
| 编译的时候提示Security Warning | Security Warning During Build |
| 链接的时候，提示无法找到⟦1⟧@xxx.objs.txt⟦/1⟧文件 | "Cannot Find ⟦1⟧@xxx.objs.txt⟦/1⟧" During Linking |
| 为什么 Code::Blocks 语法着色不对 | Why Is Code::Blocks Syntax Highlighting Wrong? |
| 工具链相关说明 | About the Toolchain |
| 为什么⟦1⟧printf⟦/1⟧无法输出浮点数 | Why Can't ⟦1⟧printf⟦/1⟧ Print Floating-Point Numbers? |
| 为什么找不到 vsprintf, sprintf, vprintf | Why Are vsprintf, sprintf and vprintf Not Found? |
| 关于调用了未声明函数的警告 | About Warnings for Calls to Undeclared Functions |
| 浮点数相关FAQ | Floating-Point FAQ |
| 如何合并⟦1⟧.a⟦/1⟧文件 | How to Merge ⟦1⟧.a⟦/1⟧ Files |
| 如何将缩减 ⟦1⟧.a⟦/1⟧ 文件里面 ⟦2⟧.o⟦/2⟧ 文件的个数 | How to Reduce the Number of ⟦2⟧.o⟦/2⟧ Files in an ⟦1⟧.a⟦/1⟧ File |
| 如何查看程序的空间使用情况 | How to View the Program's Memory Usage |
| 查看总体情况（即每个段的大小） | Viewing the Overall Usage (Size of Each Section) |
| 查看使用细节，即每个函数、变量的大小 | Viewing the Details (Size of Each Function and Variable) |
| 为什么链接时提示 stack size limit exceeded 警告 | Why Does Linking Warn "stack size limit exceeded"? |
| 常见的编译出错原因 | Common Causes of Build Errors |
| 如何在Windows系统减少编译时间 | How to Reduce Build Time on Windows |
| LINUX下安装杰理工具链和编译静态库 | Installing the Jieli Toolchain and Building Static Libraries on Linux |
| isd_config.ini 配置文件说明 | The isd_config.ini Configuration File |
| FLASH 参数配置说明 | FLASH Parameter Configuration |
| 下载目录工具说明 | Download Directory Tools |
| fat_image_tool工具介绍 | The fat_image_tool Utility |
| FLASH参数说明 | FLASH Parameters |
| 杰理科技强制升级工具4.0使用说明 | Jieli Forced Upgrade Tool 4.0 User Guide |
| 升级与下载说明 | Upgrading and Downloading |
| 灯的状态说明 | LED Status |
| 工具拨码开关说明 | Tool DIP Switches |
| 工具自身固件如何更新 | Updating the Tool's Own Firmware |
| 虚拟串口 | Virtual Serial Port |
| 如何将 Code::Blocks 工程转换为 make/VSCode 工程 | How to Convert a Code::Blocks Project to a make/VSCode Project |
| 在已经有了标准 SDK 工程的情况下，如何获得编译库的工程 | How to Get a Library Project from an Existing Standard SDK Project |
| 如何给 SDK 工程添加第三方库 | How to Add a Third-Party Library to an SDK Project |
| 为什么有些 SDK 编译很慢 | Why Are Some SDKs Slow to Build? |
| 为什么编译得到的文件不一致 | Why Do Builds Produce Different Files? |
| 为什么无法下载程序 | Why Can't the Program Be Downloaded? |
| 如何修改临时目录 | How to Change the Temporary Directory |
| 关于工具（误）报毒问题 | About Antivirus (False) Alarms on the Tools |
| 如何确认当前工程使用的下载脚本 ⟦1⟧download.bat⟦/1⟧ 是哪个 | How to Find Which ⟦1⟧download.bat⟦/1⟧ Script the Current Project Uses |
| 如何在下载前对芯片进行全擦除 | How to Fully Erase the Chip Before Downloading |
| 如何在下载后自动复位芯片 | How to Reset the Chip Automatically After Downloading |
| 如何读取芯片的 FLASH ID | How to Read the Chip's FLASH ID |
| 固件文件相关工具 | Firmware File Tools |
| 固件文件下载 | Firmware File Download |
| 固件升级工具（一拖一PC下载工具） | Firmware Upgrade Tool (1-to-1 PC Download Tool) |
| 配置项说明 | Configuration Items |
| 合并固件文件到工具 | Merging the Firmware File into the Tool |
| PC模式设备名字配置 | PC-Mode Device Name |
| PID显示和匹配规则配置 | PID Display and Matching Rules |
| 升级选项配置 | Upgrade Options |
| 窗口标题栏文字和图标配置 | Window Title Bar Text and Icon |
| 固件文件选择栏文字和文件类型 | Firmware File Selector Text and File Types |
| 自定义版本信息配置 | Custom Version Information |
| 固件信息显示配置 | Firmware Information Display |
| 样机信息显示配置 | Device Information Display |
| 自定描述信息配置 | Custom Description Text |
| 升级和校验按钮文字配置 | Upgrade and Verify Button Text |
| 认证码配置 | Authentication Code Configuration |
| 固件编辑工具说明 | Firmware Editing Tool |
| 概述 | Overview |
| 权限说明 | Permissions |
| 蓝牙名修改 | Changing the Bluetooth Name |
| 提示音替换 | Replacing Prompt Tones |
| EQ配置替换 | Replacing the EQ Configuration |
| 预留区域文件替换 | Replacing Reserved-Area Files |
| 自定义文件替换 | Replacing Custom Files |
| 配置信息更新工具说明 | Configuration Update Tool |
| 连接模式说明 | Connection Modes |
| 打开选项说明 | Open Options |
| 更新蓝牙地址说明 | Updating the Bluetooth Address |
| 更新蓝牙名说明 | Updating the Bluetooth Name |
| 更新认证码说明 | Updating Authentication Codes |
| 常见问题与解决方法 | FAQs and Solutions |
| 读取固件校验码相关问题 | Reading the Firmware Checksum |
| 文件说明 | File Types Explained |
| 杰理科技一拖二烧录器用户手册 | Jieli 1-to-2 Programmer User Manual |
| 烧录器简要介绍 | Programmer Overview |
| 手动烧录、校验、查空芯片操作流程 | Manual Programming, Verification and Blank Check |
| 机台自动烧录操作流程 | Automated Programming with a Handler |
| 远程升级烧录器固件 | Remote Upgrade of the Programmer Firmware |
| 各型号芯片PC端烧录配置项介绍 | PC-Side Programming Options for Each Chip Model |
| 状态指示和报错提示说明 | Status Indicators and Error Messages |
| 授权烧录次数限制功能 | Authorized Programming Count Limit |
| 第三方数据（认证码）烧录功能 | Programming Third-Party Data (Authentication Codes) |
| 蓝牙地址及名字自增功能 | Bluetooth Address and Name Auto-Increment |
| 芯片烧录接线和供电说明 | Chip Programming Wiring and Power Supply |
| 其它常见功能配置和使用说明 | Other Common Features: Configuration and Use |
| 常见错误处理 | Troubleshooting Common Errors |
| 杰理科技一拖八烧录器用户手册 | Jieli 1-to-8 Programmer User Manual |
| PC界面报错提示说明和处理 | PC Tool Error Messages and Solutions |
| 换板时间设置及使用说明 | Board-Change Interval Setting |
| 不同芯片烧录电压说明 | Programming Voltages for Different Chips |
| 电流功耗测试功能 | Current and Power Consumption Test |
| 样机带电池烧录 | Programming Devices with Batteries Attached |
| 频偏校准功能 | Frequency Offset Calibration |
| MIC 测试功能 | MIC Test |
| 样机带电池自定义IO单双线串口升级功能 | Upgrading Battery-Powered Devices over a Custom-IO Single/Two-Wire UART |
| 同时升级内置flash和外挂flash | Upgrading Internal and External Flash Together |
| 非全片擦除功能 | Partial (Non-Full-Chip) Erase |
| 杰理科技一拖二蓝牙测试盒用户手册 | Jieli 1-to-2 Bluetooth Test Box User Manual |
| 测试盒简要介绍 | Test Box Overview |
| 上位机功能配置和使用 | PC Tool Configuration and Use |
| 测试盒固件升级 | Test Box Firmware Upgrade |
| 蓝牙设备无线升级流程 | Wireless Upgrade of Bluetooth Devices |
| 蓝牙设备有线升级流程 | Wired Upgrade of Bluetooth Devices |
| 蓝牙设备测试流程使用说明 | Bluetooth Device Test Procedure |
| 测试盒批量升级、测试用例介绍 | Test Box Batch Upgrade and Test Cases |
| 耳机仓储模式使用方法 | Using Earphone Storage Mode |
| PC透传命令、自定义命令使用 | PC Passthrough Commands and Custom Commands |
| 测试盒MES LOG输出功能 | Test Box MES Log Output |
| 蓝牙设备信息（sdk 版本/电量/校验码）查看方法 | Viewing Bluetooth Device Information (SDK Version/Battery Level/Checksum) |
| 测试盒ufw文件校验码匹配 | Test Box UFW File Checksum Matching |
| 测试盒串口连接治具介绍 | Connecting the Test Box to a Fixture over UART |
| 其它常见功能配置和使用 | Other Common Features: Configuration and Use |
| 常见问题（FAQ）处理 | Frequently Asked Questions (FAQ) |
| 版本信息 | Version Information |
| 多算法授权使用说明 | Multi-Algorithm Authorization Guide |
| 多算法授权介绍 | Introduction to Multi-Algorithm Authorization |
| 算法提供商需要做的事情 | What Algorithm Providers Need to Do |
| 生产商需要做的事情 | What Manufacturers Need to Do |
| 杰理服务器使用方式 | Using the Jieli Server |
| 支持的芯片型号和授权执行文件工程模板 | Supported Chip Models and Authorization Executable Project Templates |
| 如何生成只有包含授权执行文件的FW | How to Generate a FW Containing Only the Authorization Executable |
| 私有数据授权使用说明 | Private Data Authorization Guide |
| SDK修改 | SDK Changes |
| 秘钥使用示例 | Key Usage Example |
| 通用功能配置和使用说明 | General Features: Configuration and Use |
| 常见isd_config.ini配置和烧录相关功能使用说明 | Common isd_config.ini Settings and Programming-Related Features |
| 如何在生成烧录文件时设置专家选项 | How to Set Expert Options When Generating a Programming File |
| 如何在生成烧录文件时设置烧录选项 | How to Set Programming Options When Generating a Programming File |
| 固件文件KEY与烧录器KEY不匹配 | Firmware File KEY Does Not Match the Programmer KEY |
| 烧录器未授权烧录当前芯片型号 | Programmer Not Authorized for the Current Chip Model |
| 版本不匹配错误 | Version Mismatch Error |
| KEY错误或不匹配 | KEY Error or Mismatch |
| TWS配对地址分析工具 | TWS Pairing Address Analysis Tool |
| 相关配置（蓝牙名、蓝牙地址、SN码）扫码更新工具 | Barcode-Scan Configuration Update Tool (Bluetooth Name, Bluetooth Address, SN) |
| FindMy 产测工具套件 | FindMy Production Test Tool Suite |
| 工具最新版本 | Latest Tool Versions |
| 如何使用 .jlxproj 文件来升级工具 | How to Upgrade Tools with a .jlxproj File |
| 如何更新工具 | How to Update the Tools |
| Code::Blocks 使用说明以及常见问题处理 | Code::Blocks Usage and Troubleshooting |
| 常见问题以及处理方法 | Common Issues and Solutions |
| 其它常见问题以及处理方法 | Other Common Issues and Solutions |
| 常见错误处理方式 | Common Errors and Solutions |

Menu sections: 程序开发相关工具 = Development Tools; 固件文件处理工具 = Firmware File Processing Tools; 量产相关工具 = Mass Production Tools; 其它工具 = Other Tools; 其它信息 = Other Information
