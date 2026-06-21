# 签证ai材料预审问题
1. 【修复】户口本户籍页和本人页 分片合并逻辑错误
2. 【修复】身份证轻微反光也会导致校验不通过
3. 【临时修复】学信网证明，pdf 转图片导致文字缺失 -》校验不通过
4. 小二后台把给用户的结果提示，也加上渲染。以及任务详情页加上bizid
5. 有户籍页：4502099234006001106_4511722060947，但结果说没有
6. 线程数一直在升，感觉有问题，dump下数据查一下：`sidji`
	![[IMG-20260315225444554.png|565]]
7. 户口本用户上传错误：
8. 点击拿地价
9. 单据大家
	```java
	@Slf4j
	@Component
	public class VisaAssistantAiAskHomePageStaticConfigManger extends AbstractFceStaticDataConfigManger {
    /**
     * 获取首页数据配置
     * @return 首页数据配置
     */
    public VisaAssistantAiAskHomePageConfig getHomepageData() {
        try {
            return super.getData(FceStaticDataIdConstant.VISA_ASSISTANT_AI_ASK_HOME_PAGE_STATIC_CONFIG_ID, VisaAssistantAiAskHomePageConfig.class);
        } catch (Exception e) {
            log.error("流量充值频道页获取静态数据失败", e);
        }
        return null;
    }
	}
	```
10. 是的
	```c
	wdwdwd
	dwwd
	```
11. dhuwh
	1. sisi
		```java
		@Slf4j
		@Component
		public class VisaAssistantAiAskHomePageStaticConfigManger extends AbstractFceStaticDataConfigManger {
		    /**
		     * 获取首页数据配置
		     * @return 首页数据配置
		     */
		    public VisaAssistantAiAskHomePageConfig getHomepageData() {
		        try {
		            return super.getData(FceStaticDataIdConstant.VISA_ASSISTANT_AI_ASK_HOME_PAGE_STATIC_CONFIG_ID, VisaAssistantAiAskHomePageConfig.class);
		        } catch (Exception e) {
		            log.error("流量充值频道页获取静态数据失败", e);
		        }
		        return null;
		    }
		}
		```
	2.
	```java
	@Slf4j
	@Component
	public class VisaAssistantAiAskHomePageStaticConfigManger extends AbstractFceStaticDataConfigManger {
	    /**
	     * 获取首页数据配置
	     * @return 首页数据配置
	     */
	    public VisaAssistantAiAskHomePageConfig getHomepageData() {
	        try {
	            return super.getData(FceStaticDataIdConstant.VISA_ASSISTANT_AI_ASK_HOME_PAGE_STATIC_CONFIG_ID, VisaAssistantAiAskHomePageConfig.class);
	        } catch (Exception e) {
	            log.error("流量充值频道页获取静态数据失败", e);
	        }
	        return null;
	    }
	}
	```

线程数

![[IMG-20260409211932833.png]]