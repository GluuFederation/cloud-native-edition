import pygluu.kubernetes.terminal.redis as module0


def test_prompt_redis_type(monkeypatch, settings):
    from pygluu.kubernetes.terminal.redis import PromptRedis

    monkeypatch.setattr("click.prompt", lambda x, default: "CLUSTER")

    settings.set("config.configmap.cnRedisType", "")
    prompt = PromptRedis(settings)
    prompt.prompt_redis()
    assert settings.get("config.configmap.cnRedisType") == "CLUSTER"


def test_redis_object_prompt():
    var0 = None
    var1 = module0.PromptRedis(var0)
    assert var1 is not None


def test_configmap_redis_prompt():
    var0 = None
    var1 = module0.PromptRedis(var0)
    assert var1 is not None
    var2 = module0.PromptRedis(var1)
    assert var2 is not None


def test_masternodes_prompt():
    var0 = None
    var1 = module0.PromptRedis(var0)
    assert var1 is not None
    var2 = module0.PromptRedis(var1)
    assert var2 is not None
    var3 = 1716
    var4 = module0.PromptRedis(var3)
    assert var4 is not None


def test_nodespermaster_prompt():
    var0 = None
    var1 = module0.PromptRedis(var0)
    assert var1 is not None
    var2 = module0.PromptRedis(var1)
    assert var2 is not None
    var3 = None
    var4 = module0.PromptRedis(var3)
    assert var4 is not None
    var5 = module0.PromptRedis(var4)
    assert var5 is not None
    var6 = 1716
    var7 = module0.PromptRedis(var6)
    assert var7 is not None
    var8 = module0.PromptRedis(var0)
    assert var8 is not None
