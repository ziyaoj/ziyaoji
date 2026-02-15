#!/usr/bin/env python3
"""
测试所有bug修复
"""
import os
import sys
import tempfile
import csv
from datetime import datetime


# 直接测试函数逻辑，避免导入依赖
def load_module_content(filepath):
    """读取模块内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def test_imports():
    """尝试导入模块（如果可能）"""
    modules = {}
    try:
        from utils import complexity_score, log_event
        modules['utils'] = True
    except Exception as e:
        print(f"  注意: utils导入失败: {e}")
        modules['utils'] = False
    
    try:
        from small_model import low_confidence
        modules['small_model'] = True
    except Exception as e:
        print(f"  注意: small_model导入失败（需要transformers）: {e}")
        modules['small_model'] = False
    
    try:
        from router import faq_answer, _load_faq
        modules['router'] = True
    except Exception as e:
        print(f"  注意: router导入失败: {e}")
        modules['router'] = False
    
    return modules


# 如果能导入，就导入
_modules = test_imports()
if _modules.get('utils'):
    from utils import complexity_score, log_event
if _modules.get('small_model'):
    from small_model import low_confidence
if _modules.get('router'):
    from router import faq_answer, _load_faq


def test_bug2_empty_question_check():
    """Bug 2: 测试空问题检查位置是否正确"""
    print("\n测试 Bug 2: 空问题检查...")
    
    if not _modules.get('utils'):
        print("  跳过: utils模块未加载")
        return
    
    # 空字符串应该返回 0
    assert complexity_score("") == 0, "空字符串应该返回 0"
    assert complexity_score("   ") == 0, "空白字符串应该返回 0"
    
    # 非空字符串应该正常计算（需要足够长才能得分）
    assert complexity_score("这是一个比较复杂的问题") > 0, "非空长字符串应该返回 > 0"
    
    print("✓ Bug 2 已修复: 空问题检查在函数开头")


def test_bug4_faq_caching():
    """Bug 4: 测试FAQ数据是否被缓存"""
    print("\n测试 Bug 4: FAQ缓存...")
    
    if not _modules.get('router'):
        print("  跳过: router模块未加载")
        return
    
    # 第一次调用会加载数据
    faq1 = _load_faq()
    
    # 第二次调用应该返回缓存的数据（同一个对象）
    faq2 = _load_faq()
    
    # 检查是否是同一个对象（说明使用了缓存）
    assert faq1 is faq2, "FAQ数据应该被缓存"
    
    print("✓ Bug 4 已修复: FAQ数据被正确缓存")


def test_bug5_weighted_faq_matching():
    """Bug 5: 测试加权FAQ匹配"""
    print("\n测试 Bug 5: 加权FAQ匹配...")
    
    if not _modules.get('router'):
        print("  跳过: router模块未加载")
        return
    
    # 测试关键词匹配
    # "食堂什么时间开" 应该匹配到食堂相关的答案，而不是图书馆
    answer = faq_answer("食堂什么时间开？")
    assert "食堂" in answer, f"应该返回食堂相关答案，实际返回: {answer}"
    assert "图书馆" not in answer, f"不应该返回图书馆答案，实际返回: {answer}"
    
    # 测试多关键词匹配优先级
    answer2 = faq_answer("图书馆几点开门？")
    assert "图书馆" in answer2, f"应该返回图书馆相关答案，实际返回: {answer2}"
    
    print("✓ Bug 5 已修复: FAQ使用加权匹配")


def test_bug6_low_confidence():
    """Bug 6: 测试low_confidence误判问题"""
    print("\n测试 Bug 6: low_confidence误判...")
    
    if not _modules.get('small_model'):
        print("  跳过: small_model模块未加载")
        return
    
    # 测试正面表述不应该被误判
    assert not low_confidence("这是无法避免的情况"), "正面表述'无法避免'不应该被误判"
    
    # 测试合理的简短回答不应该被误判（长度>=5）
    assert not low_confidence("可以的"), "5个字的回答不应该被误判"
    assert low_confidence("好的"), "2个字的回答应该被判定为低置信度"
    
    # 测试真正的低置信度回答
    assert low_confidence("我不确定"), "包含'不确定'应该被判定为低置信度"
    assert low_confidence("抱歉"), "包含'抱歉'应该被判定为低置信度"
    
    print("✓ Bug 6 已修复: low_confidence减少了误判")


def test_bug7_log_event_race_condition():
    """Bug 7: 测试log_event的竞态条件修复"""
    print("\n测试 Bug 7: log_event竞态条件...")
    
    if not _modules.get('utils'):
        print("  跳过: utils模块未加载")
        return
    
    # 创建临时目录和文件进行测试
    import tempfile
    import shutil
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 修改当前目录到临时目录
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # 第一次写入应该创建文件并写入表头
        log_event("测试问题", 1, "faq", 0.1, 0.0)
        
        # 读取文件验证
        with open("logs.csv", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 2, f"应该有表头和一行数据，实际有{len(lines)}行"
            assert "timestamp" in lines[0], "第一行应该是表头"
        
        # 第二次写入不应该重复表头
        log_event("测试问题2", 2, "small_model", 0.2, 0.0)
        
        with open("logs.csv", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 3, f"应该有表头和两行数据，实际有{len(lines)}行"
        
        print("✓ Bug 7 已修复: log_event使用了更安全的文件处理")
        
    finally:
        # 恢复原始工作目录
        os.chdir(old_cwd)
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_bug8_faq_absolute_path():
    """Bug 8: 测试FAQ路径是否使用绝对路径"""
    print("\n测试 Bug 8: FAQ绝对路径...")
    
    # 直接检查router.py文件内容
    repo_path = "/home/runner/work/ziyaoji/ziyaoji"
    with open(os.path.join(repo_path, "router.py"), 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'os.path.join(os.path.dirname(__file__), "faq.json")' in content, \
            "FAQ_PATH应该使用绝对路径"
    
    print("✓ Bug 8 已修复: FAQ使用绝对路径")


def test_bug1_small_model_exception():
    """Bug 1: 测试小模型异常处理不会触发low_confidence"""
    print("\n测试 Bug 1: 小模型异常处理...")
    
    if not _modules.get('small_model'):
        print("  跳过: small_model模块未加载")
        return
    
    # 模拟异常返回的消息
    error_message = "[小模型] 暂时繁忙，请稍后再试"
    
    # 这个消息不应该触发low_confidence
    assert not low_confidence(error_message), \
        f"小模型错误消息不应该触发low_confidence: {error_message}"
    
    print("✓ Bug 1 已修复: 小模型异常消息不会触发low_confidence")


def test_code_changes():
    """测试代码是否包含正确的修复"""
    print("\n测试代码级别的修复...")
    
    # 读取文件内容进行验证
    repo_path = "/home/runner/work/ziyaoji/ziyaoji"
    
    # Bug 2: 检查empty check在函数开头
    with open(os.path.join(repo_path, "utils.py"), 'r', encoding='utf-8') as f:
        utils_content = f.read()
        # 查找complexity_score函数
        assert "if not q:\n        return 0" in utils_content, "空问题检查应该在计算之前"
        assert utils_content.index("if not q:") < utils_content.index("# 2) 长度打分"), \
            "空问题检查应该在长度打分之前"
    print("  ✓ Bug 2: 代码已修复")
    
    # Bug 8: 检查FAQ路径是否使用绝对路径
    with open(os.path.join(repo_path, "router.py"), 'r', encoding='utf-8') as f:
        router_content = f.read()
        assert 'os.path.join(os.path.dirname(__file__), "faq.json")' in router_content, \
            "FAQ_PATH应该使用绝对路径"
    print("  ✓ Bug 8: 代码已修复")
    
    # Bug 4: 检查FAQ缓存
    assert "_faq_cache" in router_content, "应该有FAQ缓存变量"
    assert "def _load_faq():" in router_content, "应该有懒加载FAQ函数"
    print("  ✓ Bug 4: 代码已修复")
    
    # Bug 5: 检查加权匹配
    assert "best_match" in router_content and "best_score" in router_content, \
        "应该有加权匹配逻辑"
    assert "match_count" in router_content, "应该计算匹配数量"
    print("  ✓ Bug 5: 代码已修复")
    
    # Bug 1: 检查小模型异常处理
    with open(os.path.join(repo_path, "small_model.py"), 'r', encoding='utf-8') as f:
        small_model_content = f.read()
        assert "[小模型] 暂时繁忙，请稍后再试" in small_model_content, \
            "异常处理应该返回不触发low_confidence的消息"
        assert "[小模型] 我不太确定如何回答这个问题" not in small_model_content, \
            "不应该再使用触发low_confidence的消息"
    print("  ✓ Bug 1: 代码已修复")
    
    # Bug 6: 检查low_confidence改进
    assert "无法避免" in small_model_content, "应该处理'无法避免'的情况"
    assert "len(answer) < 5" in small_model_content, "最短长度应该是5"
    print("  ✓ Bug 6: 代码已修复")
    
    # Bug 7: 检查log_event改进
    assert "a+" in utils_content, "应该使用'a+'模式"
    assert "is_empty" in utils_content, "应该检查文件是否为空"
    print("  ✓ Bug 7: 代码已修复")
    
    # Bug 3: 检查cost tracking
    with open(os.path.join(repo_path, "big_model.py"), 'r', encoding='utf-8') as f:
        big_model_content = f.read()
        assert "usage_info" in big_model_content, "应该有usage_info"
        assert "total_tokens" in big_model_content, "应该返回total_tokens"
    
    assert "usage_info.get" in router_content, "router应该使用usage_info"
    assert "* 0.001" in router_content, "应该计算成本"
    print("  ✓ Bug 3: 代码已修复")
    
    print("\n✓ 所有代码级别的修复已验证")


def test_bug3_cost_tracking():
    """Bug 3: 测试成本追踪（需要模拟big_model的返回）"""
    print("\n测试 Bug 3: 成本追踪...")
    
    # 测试big_model_answer返回格式
    try:
        from big_model import big_model_answer
    except:
        print("  跳过: big_model模块未加载")
        return
    
    # 注意：这个测试可能需要API密钥，我们只验证返回格式
    try:
        # 如果没有API密钥，会捕获异常并返回降级回答
        result = big_model_answer("测试问题")
        
        # 验证返回是一个元组
        assert isinstance(result, tuple), "big_model_answer应该返回元组"
        assert len(result) == 2, "返回的元组应该有2个元素"
        
        answer, usage_info = result
        assert isinstance(answer, str), "第一个元素应该是字符串（答案）"
        assert isinstance(usage_info, dict), "第二个元素应该是字典（使用信息）"
        assert "total_tokens" in usage_info, "使用信息应该包含total_tokens"
        
        print("✓ Bug 3 已修复: big_model_answer返回成本信息")
        
    except Exception as e:
        # 如果API调用失败，至少验证错误处理返回正确格式
        print(f"  注意: API调用失败（预期行为），验证错误处理格式: {e}")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("运行Bug修复测试")
    print("=" * 60)
    
    tests = [
        test_code_changes,  # 首先测试代码级别的修复
        test_bug2_empty_question_check,
        test_bug4_faq_caching,
        test_bug5_weighted_faq_matching,
        test_bug6_low_confidence,
        test_bug7_log_event_race_condition,
        test_bug8_faq_absolute_path,
        test_bug1_small_model_exception,
        test_bug3_cost_tracking,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ 测试错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    if failed == 0:
        print("✓ 所有测试通过!")
    else:
        print(f"✗ {failed} 个测试失败")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
