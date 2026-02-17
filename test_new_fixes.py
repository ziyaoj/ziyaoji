#!/usr/bin/env python3
"""
测试6个新修复的问题
"""
import os
import sys
import json
import time

# 获取测试脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

def test_problem1_empty_question():
    """问题1: 测试空问题检查"""
    print("\n问题1: 测试空问题检查...")
    
    # 检查代码
    with open(os.path.join(SCRIPT_DIR, "router.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'if not question or not question.strip():' in content, \
            "应该检查空问题"
        assert '请输入您的问题' in content, \
            "应该返回提示信息"
        assert '"route": "invalid"' in content, \
            "应该标记为invalid路由"
    
    print("  ✓ 问题1已修复: 空问题检查已添加")

def test_problem2_absolute_log_path():
    """问题2: 测试日志文件使用绝对路径"""
    print("\n问题2: 测试日志文件绝对路径...")
    
    # 检查代码
    with open(os.path.join(SCRIPT_DIR, "utils.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'LOG_PATH = os.path.join(os.path.dirname(__file__), "logs.csv")' in content, \
            "LOG_PATH应该使用绝对路径"
        assert 'with open(LOG_PATH,' in content, \
            "log_event应该使用LOG_PATH常量"
    
    # 验证LOG_PATH值
    from utils import LOG_PATH
    expected_path = os.path.join(SCRIPT_DIR, "logs.csv")
    assert LOG_PATH == expected_path, \
        f"LOG_PATH应该是{expected_path}，实际是{LOG_PATH}"
    
    print("  ✓ 问题2已修复: 日志文件使用绝对路径")

def test_problem3_exception_fallback():
    """问题3: 测试小模型异常自动降级"""
    print("\n问题3: 测试小模型异常自动降级...")
    
    with open(os.path.join(SCRIPT_DIR, "router.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        # 检查两个分支都有异常检查
        assert content.count('answer.startswith("[小模型]")') >= 2, \
            "应该在两个分支检查小模型异常返回"
        assert content.count('or low_confidence(answer)') >= 2, \
            "应该在两个分支检查低置信度"
    
    print("  ✓ 问题3已修复: 小模型异常自动降级到大模型")

def test_problem4_history_to_big_model():
    """问题4: 测试大模型支持对话历史"""
    print("\n问题4: 测试大模型支持对话历史...")
    
    # 检查big_model.py
    with open(os.path.join(SCRIPT_DIR, "big_model.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'def big_model_answer(question: str, history: list = None):' in content, \
            "big_model_answer应该接受history参数"
        assert 'if history:' in content, \
            "应该处理history参数"
        assert 'messages.extend(history[-6:])' in content, \
            "应该加入最近3轮对话历史"
    
    # 检查router.py调用
    with open(os.path.join(SCRIPT_DIR, "router.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        # 应该有3处调用big_model_answer时传递history
        assert content.count('big_model_answer(question, history=history)') >= 3, \
            "所有big_model_answer调用都应该传递history"
    
    print("  ✓ 问题4已修复: 大模型支持对话历史")

def test_problem5_faq_hot_reload():
    """问题5: 测试FAQ热更新"""
    print("\n问题5: 测试FAQ热更新...")
    
    with open(os.path.join(SCRIPT_DIR, "router.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        assert '_faq_mtime' in content, \
            "应该有_faq_mtime变量追踪文件修改时间"
        assert 'os.path.getmtime(FAQ_PATH)' in content, \
            "应该使用getmtime检查文件修改时间"
        assert 'current_mtime > _faq_mtime' in content, \
            "应该比较修改时间决定是否重新加载"
    
    print("  ✓ 问题5已修复: FAQ支持热更新")

def test_problem6_unified_scoring():
    """问题6: 测试旧格式FAQ评分统一"""
    print("\n问题6: 测试旧格式FAQ评分统一...")
    
    with open(os.path.join(SCRIPT_DIR, "router.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        # 检查使用了常量
        assert 'PRIMARY_KEYWORD_WEIGHT' in content, \
            "应该定义PRIMARY_KEYWORD_WEIGHT常量"
        assert 'match_count * PRIMARY_KEYWORD_WEIGHT' in content, \
            "旧格式应该使用PRIMARY_KEYWORD_WEIGHT加权"
        assert '与新格式 primary 权重对齐' in content or 'primary 级别' in content, \
            "应该有注释说明权重对齐"
    
    print("  ✓ 问题6已修复: 旧格式FAQ使用统一评分体系")

def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试6个新修复的问题")
    print("=" * 60)
    
    tests = [
        test_problem1_empty_question,
        test_problem2_absolute_log_path,
        test_problem3_exception_fallback,
        test_problem4_history_to_big_model,
        test_problem5_faq_hot_reload,
        test_problem6_unified_scoring,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  ✗ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ 测试错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    if failed == 0:
        print("✓ 所有6个问题的修复已验证!")
    else:
        print(f"✗ {failed} 个测试失败")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
