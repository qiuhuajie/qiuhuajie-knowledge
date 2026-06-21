---
title: "方式 1：CloseableHttpClient"
tags:
  - "计算机基础知识"
  - "计算机基础知识/计算机网络"
  - "计算机基础知识/计算机网络/应用层协议"
  - "Java 发送 HTTP 请求"
  - "计算机基础"
  - "计算机网络"
updated: 2026-04-16
---
# 一、引入依赖
```XML
<dependency>
    <groupId>org.apache.httpcomponents</groupId>
    <artifactId>httpclient</artifactId>
    <version>4.5.6</version>
</dependency>
```
# 二、Demo
```Java
public class HttpTest3 {
    public static void main(String[] args) {
        int timeout = 120000;
        CloseableHttpClient httpClient = HttpClients.createDefault();
        RequestConfig defaultRequestConfig = RequestConfig.custom().setConnectTimeout(timeout)
                .setConnectionRequestTimeout(timeout).setSocketTimeout(timeout).build();
        HttpPost httpPost = null;
        List<NameValuePair> nvps = null;
        CloseableHttpResponse responses = null;// 命名冲突，换一个名字，response
        HttpEntity resEntity = null;
        String result;
        try {
            httpPost = new HttpPost("http://10.30.10.151:8012/gateway.do");
            httpPost.setConfig(defaultRequestConfig);
            Map paraMap = new HashMap();
            paraMap.put("type", "wx");
            paraMap.put("mchid", "10101");
            nvps = new ArrayList<NameValuePair>();
            nvps.add(new BasicNameValuePair("consumerAppId", "test"));
            nvps.add(new BasicNameValuePair("serviceName", "queryMerchantService"));
            nvps.add(new BasicNameValuePair("params", JSON.toJSONString(paraMap)));
            httpPost.setEntity(new UrlEncodedFormEntity(nvps, Consts.UTF_8));
            responses = httpClient.execute(httpPost);
            resEntity = responses.getEntity();
            result = EntityUtils.toString(resEntity, Consts.UTF_8);
            EntityUtils.consume(resEntity);
            System.out.println("result:" + result);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                responses.close();
                httpClient.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
```
