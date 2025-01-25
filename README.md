# Whop Store Generator Bot

一个自动响应Twitter提及并生成Whop商店的Twitter机器人。

## 功能描述

该机器人可以:
1. 监听Twitter上的@GenerateWhop提及
2. 解析推文内容，提取关键信息
3. 自动生成Whop商店，包括:
   - 商店logo生成
   - 描述文本生成
   - Bold claim生成
   - 添加基础的chat应用
   - 基于推文内容填充所有必需字段
4. 回复原始推文，提供新创建的Whop商店链接

## 技术架构

- Python 3.9+
- 主要依赖:
  - tweepy: Twitter API交互
  - openai: 文本生成
  - requests: API请求
  - Pillow: 图像处理
  - python-dotenv: 环境变量管理

## 项目结构 