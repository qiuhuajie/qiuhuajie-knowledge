# 一、SSE 的本质

* 服务器向浏览器推送信息，除了 [WebSocket](https://www.ruanyifeng.com/blog/2017/05/websocket.html)，还有一种方法：Server-Sent Events，以下简称 SSE。本文介绍它的用法。

    ![[Attachment/4a697cf050200d82f430bc7684a36a79_MD5.png|500]]

1. 严格地说，[HTTP 协议](https://www.ruanyifeng.com/blog/2016/08/http.html)无法做到服务器主动推送信息，但是可以通过一种变通方法来实现，也就是服务器向客户端声明，接下来要发送的是流信息（streaming）。
2. 发送的不是一次性的数据包，而是一个连续不断发送的数据流。这时，客户端不会关闭连接，而是一直等待服务器发来的新数据流。视频播放就是这种机制的典型例子，本质上它是以流信息的方式完成一次耗时较长的下载。
3. SSE 就是利用这种机制，使用流信息向浏览器推送信息。它基于 HTTP 协议，目前除了 IE / Edge，其他浏览器都支持。

# 二、SSE 的特点

1. SSE 与 WebSocket 的作用相似，都是建立浏览器与服务器之间的通信渠道，然后由服务器向浏览器推送信息。
2. 总体来说，WebSocket 更强大也更灵活，因为它是全双工通道，可以双向通信；SSE 是单向通道，只能由服务器向浏览器发送信息，因为流信息本质上就是下载。如果浏览器向服务器发送信息，就会变成另一次 HTTP 请求。

    ![[Attachment/4aa7ffee89963ea51d2828d258155235_MD5.jpg|500]]

3. 不过，SSE 也有自己的优点。
    * SSE 使用 HTTP 协议，现有的服务器软件都支持；WebSocket 是独立协议。
    * SSE 属于轻量级方案，使用简单；WebSocket 协议相对复杂。
    * SSE 默认支持断线重连；WebSocket 需要自己实现。
    * SSE 一般只用来传送文本，二进制数据需要编码后传送；WebSocket 默认支持传送二进制数据。
    * SSE 支持自定义发送的消息类型。
4. 因此，两者各有特点，适合不同的场合。

# 三、客户端 API

## 1. EventSource 对象

1. SSE 的客户端 API 部署在 **`EventSource`** 对象上。下面的代码可以用来检测浏览器是否支持 SSE。

    ```javascript
    if ('EventSource' in window) {
      // ...
    }
    ```

2. 使用 SSE 时，浏览器首先会生成一个 **`EventSource`** 实例，向服务器发起连接。

    ```javascript
    var source = new EventSource(url);
    ```

3. 上面的 `url` 可以与当前网址同域，也可以跨域。跨域时可以指定第二个参数，打开 `withCredentials` 属性，表示是否一起发送 Cookie。

    ```javascript
    var source = new EventSource(url, { withCredentials: true });
    ```

4. **`EventSource`** 实例的 **`readyState`** 属性用于表明连接的当前状态。这个属性是只读的，可以取以下几个值。
    * `0`：相当于常量 **`EventSource.CONNECTING`**，表示连接还未建立，或者断线后正在重连。
    * `1`：相当于常量 **`EventSource.OPEN`**，表示连接已经建立，可以接收数据。
    * `2`：相当于常量 **`EventSource.CLOSED`**，表示连接已断，且不会重连。

## 2. 基本用法

1. 连接一旦建立，就会触发 `open` 事件，可以在 **`onopen`** 属性上定义回调函数。

    ```javascript
    source.onopen = function (event) {
      // ...
    };

    // 另一种写法
    source.addEventListener('open', function (event) {
      // ...
    }, false);
    ```

2. 客户端收到服务器发来的数据，就会触发 `message` 事件，可以在 **`onmessage`** 属性中定义回调函数。

    ```javascript
    source.onmessage = function (event) {
      var data = event.data;
      // handle message
    };

    // 另一种写法
    source.addEventListener('message', function (event) {
      var data = event.data;
      // handle message
    }, false);
    ```

3. 上面代码中，事件对象的 **`data`** 属性就是服务器端传回的数据，格式是文本。
4. 如果发生通信错误，比如连接中断，就会触发 `error` 事件，可以在 **`onerror`** 属性中定义回调函数。

    ```javascript
    source.onerror = function (event) {
      // handle error event
    };

    // 另一种写法
    source.addEventListener('error', function (event) {
      // handle error event
    }, false);
    ```

5. **`close()`** 方法用于关闭 SSE 连接。

    ```javascript
    source.close();
    ```

## 3. 自定义事件

1. 默认情况下，服务器发来的数据总是触发浏览器 **`EventSource`** 实例的 `message` 事件。开发者也可以自定义 SSE 事件，这种情况下，返回的数据不会触发 `message` 事件。

    ```javascript
    source.addEventListener('foo', function (event) {
      var data = event.data;
      // handle message
    }, false);
    ```

2. 上面代码中，浏览器对 SSE 的 `foo` 事件进行了监听。如何让服务器发送 `foo` 事件，可以看后文。

# 四、服务器实现

## 1. 数据格式

1. 服务器向浏览器发送的 SSE 数据，必须是 UTF-8 编码的文本，并且响应头需要包含下面这些 HTTP 头信息。

    ```http
    Content-Type: text/event-stream
    Cache-Control: no-cache
    Connection: keep-alive
    ```

2. 上面三行之中，第一行的 **`Content-Type`** 必须指定 MIME 类型为 **`text/event-stream`**。
3. 每一次发送的信息由若干个 `message` 组成，每个 `message` 之间用 `\n\n` 分隔；每个 `message` 内部又由若干行组成，每一行都遵循下面这种格式。

    ```text
    [field]: value\n
    ```

4. 上面的 `field` 可以取四个值。
    * `data`
    * `event`
    * `id`
    * `retry`
5. 此外，还可以有冒号开头的行，表示注释。通常服务器会每隔一段时间向浏览器发送一个注释，用来保持连接不中断。

    ```text
    : This is a comment
    ```

6. 下面是一个完整示例。

    ```text
    : this is a test stream\n\n

    data: some text\n\n

    data: another message\n
    data: with two lines \n\n
    ```

## 2. Data 字段

1. 数据内容用 `data` 字段表示。

    ```text
    data:  message\n\n
    ```

2. 如果数据很长，可以拆成多行，最后一行用 `\n\n` 结尾，前面各行都用 `\n` 结尾。

    ```text
    data: begin message\n
    data: continue message\n\n
    ```

3. 下面是一个发送 JSON 数据的例子。

    ```text
    data: {\n
    data: "foo": "bar",\n
    data: "baz", 555\n
    data: }\n\n
    ```

## 3. Id 字段

1. 数据标识符用 `id` 字段表示，相当于每一条数据的编号。

    ```text
    id: msg1\n
    data: message\n\n
    ```

2. 浏览器可以通过 **`lastEventId`** 属性读取这个值。
3. 一旦连接断线，浏览器会发送一个 HTTP 头，其中包含特殊的 **`Last-Event-ID`** 头信息，将这个值发回服务器端，用来帮助服务器重建连接。因此，这个头信息可以被看作一种同步机制。

## 4. Event 字段

1. `event` 字段表示自定义事件类型，默认是 `message` 事件。浏览器可以通过 **`addEventListener()`** 监听该事件。

    ```text
    event: foo\n
    data: a foo event\n\n

    data: an unnamed event\n\n

    event: bar\n
    data: a bar event\n\n
    ```

2. 上面的代码创造了三条信息。第一条的名字是 `foo`，会触发浏览器的 `foo` 事件；第二条没有命名，表示默认类型，会触发浏览器的 `message` 事件；第三条名字是 `bar`，会触发浏览器的 `bar` 事件。
3. 下面是另一个例子。

    ```text
    event: userconnect
    data: {"username": "bobby", "time": "02:33:48"}

    event: usermessage
    data: {"username": "bobby", "time": "02:34:11", "text": "Hi everyone."}

    event: userdisconnect
    data: {"username": "bobby", "time": "02:34:23"}

    event: usermessage
    data: {"username": "sean", "time": "02:34:36", "text": "Bye, bobby."}
    ```

## 5. Retry 字段

1. 服务器可以通过 `retry` 字段指定浏览器重新发起连接的时间间隔。

    ```text
    retry: 10000\n
    ```

2. 两种情况会导致浏览器重新发起连接：一种是时间间隔到期，另一种是由于网络错误等原因导致连接出错。

# 五、Node 服务器实例

1. SSE 要求服务器与浏览器保持连接。对于不同的服务器软件来说，消耗的资源是不一样的。Apache 服务器里每个连接就是一个线程，如果需要维持大量连接，就会消耗大量资源；Node 则是所有连接共用同一个线程，因此资源消耗会小得多。
2. 不过，这也要求每个连接不能包含很耗时的操作，比如磁盘 IO 读写。
3. 下面是 Node 的 SSE 服务器[实例](http://cjihrig.com/blog/server-sent-events-in-node-js/)。

    ```javascript
    var http = require("http");

    http.createServer(function (req, res) {
      var fileName = "." + req.url;

      if (fileName === "./stream") {
        res.writeHead(200, {
          "Content-Type":"text/event-stream",
          "Cache-Control":"no-cache",
          "Connection":"keep-alive",
          "Access-Control-Allow-Origin": '*',
        });
        res.write("retry: 10000\n");
        res.write("event: connecttime\n");
        res.write("data: " + (new Date()) + "\n\n");
        res.write("data: " + (new Date()) + "\n\n");

        interval = setInterval(function () {
          res.write("data: " + (new Date()) + "\n\n");
        }, 1000);

        req.connection.addListener("close", function () {
          clearInterval(interval);
        }, false);
      }
    }).listen(8844, "127.0.0.1");
    ```

4. 可以先将上面的代码保存为 **`server.js`**，然后执行下面的命令。

    ```bash
    $ node server.js
    ```

5. 上面的命令会在本机 `8844` 端口启动一个 HTTP 服务。
6. 然后打开这个[网页](http://jsbin.com/vuziboduwa/edit?html,output)，查看客户端代码并运行。