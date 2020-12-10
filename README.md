# short_snowflake
FORK 自 https://github.com/tarzanjw/pysnowflake
通过去除节点信息，生成 16 位数的雪花 ID
short snowflake 提供了 3 种生成模式：normal, short, radical
3 种模式支持的并发数相同，均为 4096 / ms，但是 normal 支持节点 1024 个，short 支持的节点仅 4 个，radical 为单节点
在 normal 模式下 dc 的合法区间为 0～3，worker 的合法区间为 0～255
在 short 模式下，dc 参数将不起实际作用，worker 的合法区间为 0～3
在 radical 模式下，dc 和 worker 参数都不起实际作用
short 模式的生成长度将于十几年后涨到 17 位，radical 几十年后仍然为 16 位