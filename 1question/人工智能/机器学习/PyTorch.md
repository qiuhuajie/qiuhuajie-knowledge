- [[#PyTorch 安装]]
- [[#Tensorboard 的使用]]
- [[#图像变换Transform 的使用]]
- [[#数据加载]]
- [[#DataSet]]
- [[#DataLoader]]
- [[#神经网络]]
- [[#卷积操作]]
- [[#池化操作]]
- [[#非线性激活函数]]
- [[#线性层]]
- [[#CIFAR10 小模型]]
- [[#损失函数]]
- [[#反向传播]]
- [[#优化器]]
- [[#使用现成的模型]]
- [[#模型的保存与加载]]
- [[#完整的模型训练]]
- [[#使用 GPU 训练 1]]
- [[#使用 GPU 训练 2]]
- [[#分类测试]]
# **PyTorch 安装**
1. 下载安装anaconda
    
    1. 下载地址：[https://repo.anaconda.com/archive/](https://repo.anaconda.com/archive/)
    
    1. 选择版本：[Anaconda3-5.2.0-Windows-x86_64.exe](https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe)
    
1. 创建虚拟环境
    
    ```Bash
     conda create -n pytorch_one python=3.6
     
     conda activate pytorch_one
    ```
    
1. 下载安装pytorch
    
    1. 下载地址：[https://pytorch.org/](https://pytorch.org/)
    
    1. 查看GPU型号是否支持cunda：[https://www.nvidia.cn/geforce/technologies/cuda/supported-gpus/?field_gpu_type_value=All](https://www.nvidia.cn/geforce/technologies/cuda/supported-gpus/?field_gpu_type_value=All)
    
    1. 查看DPU驱动版本与支持的cuda版本：
        
        ```Bash
         C:\Users\lenovo>cd C:\Program Files\NVIDIA Corporation\NVSMI\
         
         C:\Program Files\NVIDIA Corporation\NVSMI>nvidia-smi
        ```
        
    
    1. 选择版本：
    
    1. 安装命令：
        
        ```Plain
         conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
         
         \#视频中9.2的下载命令
         conda install pytorch torchvision cudatoolkit=9.2 -c pytorch -c defaults -c numba/label/dev
        ```
        
    
    1. 查看已下载的包：
        
        ```Plain
         (pytorch_one) C:\Windows\system32>pip list
         Package           Version
         ----------------- ---------
         certifi           2021.5.30
         dataclasses       0.8
         mkl-fft           1.3.0
         mkl-random        1.1.1
         mkl-service       2.3.0
         numpy             1.19.2
         olefile           0.46
         Pillow            8.3.1
         pip               21.2.2
         setuptools        58.0.4
         six               1.16.0
         torch             1.10.0
         torchaudio        0.10.0
         torchvision       0.11.1
         typing-extensions 3.10.0.2
         wheel             0.37.0
         wincertstore      0.2
        ```
        
    
1. 确认安装成功
    
    ```Plain
     >>> import torch
     >>>
    ```
    
1. 确认cuda正常使用：保证可以使用GPU来加速模型的训练
    
    ```Plain
     >>> import torch
     >>> torch.cuda.is_available()
     True
     >>>
    ```
    
# **Tensorboard 的使用**
1. 安装Tensorboard
    
    ```Plain
     pip install tensorboard
    ```
    
1. add_scalar 方法：
    
    1. 方法参数
        
        ```Plain
         def add_scalar(
                 self,
                 tag,    # 标题
                 scalar_value,   # y轴值 Value to save (float or string/blobname)
                 global_step=None,   # x轴值 Global step value to record
                 walltime=None,
                 new_style=False,
                 double_precision=False,
             ):
        ```
        
    
    1. 示例：
        
        ```Plain
         from torch.utils.tensorboard import SummaryWriter
         
         # log文件生成的目标目录
         writer = SummaryWriter("logs")
         
         # 画 y = x 的函数图像
         for i in range(100):
             # writer.add_scalar(标题,y轴值,x轴值）
             writer.add_scalar("y = x",i,i)
         
         writer.close()
        ```
        
    
    1. 会在logs 文件夹下生成日志文件：
    
    1. 在 Terminal 中 使用 tensorboard 查看 logs 中的日志文件
        
        ```Plain
         (pytorch_one) C:\Users\lenovo\PycharmProjects\pytorch_demo>tensorboard --logdir=logs
         TensorFlow installation not found - running with reduced feature set.
         Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all
         TensorBoard 2.7.0 at http://localhost:6006/ (Press CTRL+C to quit)
         # 提供一个web端口访问 http://localhost:6006/
        ```
        
    
    1. 访问 web
    
1. add_image 方法：
    
    1. 方法参数
        
        ```Plain
         def add_image(
             self,
             tag,    # 标题
             img_tensor,     # 图片数据，需要的类型:(torch.Tensor, numpy.array, or string/blobname)
             global_step=None, # Global step value to record
             walltime=None,
             dataformats='CHW'
         ):
        ```
        
    
    1. 如果使用 PIL 读取的文件格式：
        
        ```Plain
         from PIL import Image
         image_path = "hymenoptera_data/train/ants/0013035.jpg"
         img = Image.open(image_path)
         print(type(img))
         <class 'PIL.JpegImagePlugin.JpegImageFile'>
         
         # 这里 PIL 读取的图片数据类型是 PIL.JpegImagePlugin 类型
         # 如果要使用 add_image() 需要转为 torch.Tensor 或 numpy.array
        ```
        
    
    1. 将图片数据转化为 numpy.array 格式
        
        ```Plain
         from torch.utils.tensorboard import SummaryWriter
         import numpy as np
         from PIL import Image
         
         writer = SummaryWriter("logs")
         image_path = "hymenoptera_data/train/ants/0013035.jpg"
         
         # 使用 Image 打开图片
         img_PIL = Image.open(image_path)
         
         # 将图片数据转为 numpy.array 格式
         image_array = np.array(img_PIL)
         
         # 使用 add_image()
         # 注：需要注明 dataformats='HWC' 即数据的格式
         writer.add_image("test",image_array,1,dataformats='HWC')
         
         writer.close()
        ```
        
    
    1. 或不使用 Image 读取数据，而使用 OpenCV
        
        ```Plain
         import cv2
         cv_image = cv2.imread(image_path)
         print(type(cv_image))
         
         <class 'numpy.ndarray'>
         
         # OpenCV 直接读取的数据就是 numpy.array格式的
        ```
        
    
    1. 使用 tensorboard 查看 logs 中的日志文件
        
        ```Plain
         tensorboard --logdir=logs
        ```
        
    
# **图像变换Transform 的使用**
1. Transforms 的结构
    
    torchvision 中的 Transform 提供很多class ，支持对图片进行一些变换
    
1. Transforms 的使用（以ToTensor()为例）
    
    ```Plain
     # 源码：
     class ToTensor:
         """Convert a ``PIL Image`` or ``numpy.ndarray`` to tensor. This transform does not support torchscript.
    ```
    
    ```Plain
     # 使用示例：
     from torchvision import transforms
     from PIL import Image
     
     image_path = "hymenoptera_data/train/ants/0013035.jpg"
     
     # 使用 Image 打开图片
     image = Image.open(image_path)
     
     # new 一个 transforms 中 ToTensor 类的对象，即new一个有相应类的功能的工具
     tool = transforms.ToTensor()
     
     # 使用 工具对象 对图片进行转换操作
     image_tensor = tool(image)
     
     print(image_tensor)
    ```
    
    ```Plain
     tensor([[[0.3137, 0.3137, 0.3137,  ..., 0.3176, 0.3098, 0.2980],
              [0.3176, 0.3176, 0.3176,  ..., 0.3176, 0.3098, 0.2980],
              [0.3216, 0.3216, 0.3216,  ..., 0.3137, 0.3098, 0.3020],
              ...,
              [0.3412, 0.3412, 0.3373,  ..., 0.1725, 0.3725, 0.3529],
              [0.3412, 0.3412, 0.3373,  ..., 0.3294, 0.3529, 0.3294],
              [0.3412, 0.3412, 0.3373,  ..., 0.3098, 0.3059, 0.3294]],
     
             [[0.5922, 0.5922, 0.5922,  ..., 0.5961, 0.5882, 0.5765],
              [0.5961, 0.5961, 0.5961,  ..., 0.5961, 0.5882, 0.5765],
              [0.6000, 0.6000, 0.6000,  ..., 0.5922, 0.5882, 0.5804],
              ...,
              [0.6275, 0.6275, 0.6235,  ..., 0.3608, 0.6196, 0.6157],
              [0.6275, 0.6275, 0.6235,  ..., 0.5765, 0.6275, 0.5961],
              [0.6275, 0.6275, 0.6235,  ..., 0.6275, 0.6235, 0.6314]],
     
             [[0.9137, 0.9137, 0.9137,  ..., 0.9176, 0.9098, 0.8980],
              [0.9176, 0.9176, 0.9176,  ..., 0.9176, 0.9098, 0.8980],
              [0.9216, 0.9216, 0.9216,  ..., 0.9137, 0.9098, 0.9020],
              ...,
              [0.9294, 0.9294, 0.9255,  ..., 0.5529, 0.9216, 0.8941],
              [0.9294, 0.9294, 0.9255,  ..., 0.8863, 1.0000, 0.9137],
              [0.9294, 0.9294, 0.9255,  ..., 0.9490, 0.9804, 0.9137]]])
    ```
    
1. 为什么要转换为 tensor 数据类型？
    
    封装了 一些 反向神经网络理论参数。如：backward_hooks 和 requires_grad
    
1. 常见的 Transform 的使用
    
    1. `ToTensor()`：Convert a PIL Image or numpy.ndarray to tensor
        
        ```Plain
         from torchvision import transforms
         from PIL import Image
         
         image_path = "hymenoptera_data/train/ants/0013035.jpg"
         
         # 使用 Image 打开图片
         image = Image.open(image_path)
         
         # new 一个 transforms 中 ToTensor 类的对象，即new一个有相应类的功能的工具
         tool = transforms.ToTensor()
         
         # 使用 工具对象 对图片进行转换操作
         image_tensor = tool(image)
         
         print(image_tensor)
        ```
        
    
    1. `Normalize()`：Normalize a tensor image with mean and standard deviation
        
        ```Plain
         # 归一化的计算公式
         output[channel] = (input[channel] - mean[channel]) / std[channel]
         
         # 参数
         Args:
                 mean (sequence): Sequence of means for each channel.
                 std (sequence): Sequence of standard deviations for each channel.
                 inplace(bool,optional): Bool to make this operation in-place.
        ```
        
        ```Plain
        from torch.utils.tensorboard import SummaryWriter
        
        image_path = "hymenoptera_data/train/ants/0013035.jpg"
        
        # 使用 Image 打开图片
        image = Image.open(image_path)
        
        # new 一个 transforms 中 ToTensor 类的对象，即new一个有相应类的功能的工具
        tool = transforms.ToTensor()
        
        # 使用 工具对象 对图片进行转换操作
        image_tensor = tool(image)
        
        # 查看 [0][0][0] 数据的变化
        print(image_tensor[0][0][0]) # tensor(0.3137)
        
        # new 归一化的 tool 对象
        # Normalize() 的参数：（每一个通道的均值，每一个通道的标准差）
        normalize_tool = transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5])
        
        # 需要传入 tensor 类型的数据
        image_normalize = normalize_tool(image_tensor)
        
        print(image_normalize[0][0][0]) # tensor(-0.3725)
        
        write = SummaryWriter("logs")
        write.add_image("Nomalize",image_normalize)
        write.close()
        ```
        
    
    1. `resize()`：Resize the input image to the given size
        
        ```Plain
        from torchvision import transforms
        from PIL import Image
        from torch.utils.tensorboard import SummaryWriter
        
        image_path = "hymenoptera_data/train/ants/0013035.jpg"
        
        # 使用 Image 打开图片
        image = Image.open(image_path)
        
        print(image.size)
        resize_tool = transforms.Resize((512,512))
        image_resize = resize_tool(image)
        print(image_resize.size)
        image_resize = toTensor_tool(image_resize)
        write.add_image("image_resize",image_resize,0)
        
        write.close()
        ```
        
    
    1. `compose()`：Composes several transforms together
        
        ```Plain
        from torchvision import transforms
        from PIL import Image
        from torch.utils.tensorboard import SummaryWriter
        
        image_path = "hymenoptera_data/train/ants/0013035.jpg"
        
        # 使用 Image 打开图片
        image = Image.open(image_path)
        
        toTensor_tool = transforms.ToTensor()
        
        print(image.size) # (768, 512)
        resize_tool_2 = transforms.Resize(100)
        
        # 将上面两个 tool 合并成一个
        # 参数顺序不能变: resize_tool_2 的输出 即为 toTensor_tool 的输入
        compose_tool = transforms.Compose([resize_tool_2,toTensor_tool])
        compose_image = compose_tool(image)
        print(compose_image.size) # (100，150)
        write.add_image("image_compose",compose_image,0)
        
        write.close()
        ```
        
    
    1. `randomcrop()`：Crop the given image at a random location
        
        ```Plain
        from torchvision import transforms
        from PIL import Image
        from torch.utils.tensorboard import SummaryWriter
        
        image_path = "hymenoptera_data/train/ants/0013035.jpg"
        
        # 使用 Image 打开图片
        image = Image.open(image_path)
        
        randomCrop_tool = transforms.RandomCrop(100)
        randomCrop_toTensor_tool = transforms.Compose([randomCrop_tool,toTensor_tool])
        for i in range(10):
            image_crop = randomCrop_toTensor_tool(image)
            write.add_image("randomCrop",image_crop,i)
        
        write.close()
        ```
        
    
# **数据加载**
1. Dataset：提供一种方式取获数据及其label；告诉我们总共获得了多少数据
1. Dataloader：为后面的网络提供不同的数据形式
# **DataSet**
1. 自定义数据集
    
    ```Plain
    from torch.utils.data import Dataset
    from PIL import Image
    import os
    
    class MyData(Dataset):
        def __init__(self,root_dir,label_dir):
            self.root_dir = root_dir
            self.label_dir = label_dir
            self.path = os.path.join(self.root_dir,self.label_dir)
            self.img_path = os.listdir(self.path)
    
        def __getitem__(self, idx):
            img_name = self.img_path[idx]
            img_item_path = os.path.join(self.root_dir,self.label_dir,img_name)
            \#img_item_path = "C:\\Users\\lenovo\\PycharmProjects\\pytorch_demo\\hymenoptera_data\\train\\ants\\:"
    
            img = Image.open(img_item_path)
            label = self.label_dir
            return img,label
    
        def __len__(self):
            return len(self.img_path)
    
    root_dir = "C:\\Users\\lenovo\\PycharmProjects\\pytorch_demo\\hymenoptera_data\\train\\"
    
    ants_label_dir = "ants"
    bees_label_dir = "bees"
    
    ants_dataset = MyData(root_dir,ants_label_dir)
    bees_dataset = MyData(root_dir,bees_label_dir)
    
    # 数据集拼接
    train_dataset = ants_dataset + bees_dataset
    
    # 调用 def __getitem__(self, idx): 取出一张图片
    img,label = ants_dataset[1]
    
    # 显示图片
    img.show()
    ```
    
1. 标准数据集
    
    ```Plain
    import torchvision
    train_set = torchvision.datasets.CIFAR10(root="./dataset",train=True,download=True)
    test_set = torchvision.datasets.CIFAR10(root="./dataset",train=False,download=True)
    
    print(test_set[0])
    print(test_set.classes)
    
    img,target = test_set[0]
    print(img)
    print(target)
    print(test_set.classes[target])
    img.show()
    
    # Files already downloaded and verified
    # Files already downloaded and verified
    # (<PIL.Image.Image image mode=RGB size=32x32 at 0x21400061080>, 3)
    # ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    # <PIL.Image.Image image mode=RGB size=32x32 at 0x214000610B8>
    # 3
    # cat
    ```
    
1. 使用 Tensorboard 显示数据集
    
    ```Plain
    import torchvision
    
    # 注意 ToTensor() 括号不要丢掉
    dataset_transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])
    
    # 在下载数据集的时候就可以 使用 transform 来指定 transforms_tool
    train_set = torchvision.datasets.CIFAR10(root="./dataset",train=True,transform=dataset_transform,download=True)
    test_set = torchvision.datasets.CIFAR10(root="./dataset",train=False,transform=dataset_transform,download=True)
    
    img,target = test_set[0]
    print(img)
    from torch.utils.tensorboard import SummaryWriter
    writer = SummaryWriter("logs")
    
    for i in range(10):
        img,target = test_set[i]
        writer.add_image("dataset",img,i)
    
    writer.close()
    ```
    
# **DataLoader**
1. DataLoader 的参数：
    
    ```Plain
    # 数据集位置
    dataset (Dataset) – dataset from which to load the data.
    
    # 每次加载几个数据
    batch_size (int, optional) – how many samples per batch to load (default: 1).
    
    # 在每次加载后，是否重新打乱数据集
    shuffle (bool, optional) – set to True to have the data reshuffled at every epoch (default: False).
    
    # 每次加载使用的线程数
    num_workers (int, optional) – how many subprocesses to use for data loading. 0 means that the data will be loaded in the main process. (default: 0)
    
    # 每次按 batch_size 加载，如果有剩余，是否删除
    drop_last (bool, optional) – set to True to drop the last incomplete batch, if the dataset size is not divisible by the batch size. If False and the size of dataset is not divisible by the batch size, then the last batch will be smaller. (default: False)
    ```
    
1. 示例：
    
    ```Plain
     import torchvision
     from torch.utils.data import DataLoader
     from torch.utils.tensorboard import SummaryWriter
     
     # 数据集
     test_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor())
     
     # 数据加载器
     test_loader = DataLoader(dataset=test_set,batch_size=4,shuffle=True,num_workers=0,drop_last=True)
     
     writer = SummaryWriter("dataloader")
     step = 0
     for data in test_loader:
         imgs,targets = data
         # 注意：这里是 add_images 不是 add_image
         writer.add_images ("dataloader",imgs,step)
         step = step + 1
     
     writer.close()
    ```
    
# **神经网络**
[https://pytorch.org/docs/stable/nn.html](https://pytorch.org/docs/stable/nn.html)
1. Containers：为神经网络一个基本的骨架
    
    Base class for all neural network modules.
    
    ```Plain
     import torch.nn as nn
     import torch.nn.functional as F
     
     class Model(nn.Module):
         def __init__(self):
             super(Model, self).__init__()
             self.conv1 = nn.Conv2d(1, 20, 5)
             self.conv2 = nn.Conv2d(20, 20, 5)
     
         def forward(self, x):
             x = F.relu(self.conv1(x))
             return F.relu(self.conv2(x))
    ```
    
1. 示例：
    
    ```Plain
     import torch
     from torch import nn
     class coolcool(nn.Module):
         def __init__(self) -> None:
             super().__init__()
     
         def forward(self,input):
             output = input + 1
             return output
     cool_nn = coolcool()
     x = torch.tensor(1.0)
     output = cool_nn(x)
     
     print(output) # tensor(2.)
    ```
    
# **卷积操作**
1. 什么是卷积
    
    ```Plain
     # 卷积操作示例：
     import torch
     import torch.nn.functional as F
     
     # 输入的tensor
     input = torch.tensor([[1,2,0,3,1],
                          [0,1,2,3,1],
                          [1,2,1,0,0],
                          [5,2,3,1,1],
                          [2,1,0,1,1]])
     # 卷积核
     kernel = torch.tensor([[1,2,1],
                            [0,1,0],
                            [2,1,0]])
     
     input = torch.reshape(input,(1,1,5,5))
     kernel = torch.reshape(kernel,(1,1,3,3))
     
     print(input.shape)
     print(kernel.shape)
     
     output = F.conv2d(input,kernel,stride=1)
     print(output)
     
     output = F.conv2d(input,kernel,stride=2)
     print(output)
     
     output = F.conv2d(input,kernel,stride=1,padding=1)
     print(output)
     
     # 结果：
     
     # torch.Size([1, 1, 5, 5])
     
     # torch.Size([1, 1, 3, 3])
     
     # tensor([[[[10, 12, 12],
     #           [18, 16, 16],
     #           [13,  9,  3]]]])
     
     # tensor([[[[10, 12],
     #           [13,  3]]]])
     
     # tensor([[[[ 1,  3,  4, 10,  8],
     #           [ 5, 10, 12, 12,  6],
     #           [ 7, 18, 16, 16,  8],
     #           [11, 13,  9,  3,  4],
     #           [14, 13,  9,  7,  4]]]])
     
    ```
    
    1. 不额外设置填充 padding = 0，stride = 1
    
    1. 不额外设置填充 padding = 0，stride = 2
    
    1. 额外设置填充 padding = 1（填充值为0），stride = 1
    
1. 二维卷积 torch.nn.Conv2d
    
    1. 参数
        
        - **in_channels** ([_int_](https://docs.python.org/3/library/functions.html#int)) – Number of channels in the input image
        
        - **out_channels** ([_int_](https://docs.python.org/3/library/functions.html#int)) – Number of channels produced by the convolution
        
        - **kernel_size** ([_int_](https://docs.python.org/3/library/functions.html#int) _or_ [_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple)) – Size of the convolving kernel
        
        - **stride** ([_int_](https://docs.python.org/3/library/functions.html#int) _or_ [_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple)_, optional_) – Stride of the convolution. Default: 1
        
        - **padding** ([_int_](https://docs.python.org/3/library/functions.html#int)_,_ [_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple) _or_ [_str_](https://docs.python.org/3/library/stdtypes.html#str)_, optional_) – Padding added to all four sides of the input. Default: 0
        
        - **dilation** – the spacing between kernel elements. Can be a single number or a tuple (dH, dW). Default: 1
            
            dilation：空洞卷积，Default: 1 默认不使用
            
        
        1. in_channels：输入图片的通道数
        
        1. out_channels：可以设置多个卷积核，这样就会输出多个结果
        
        1. kernel_size：卷积核的大小
        
        1. stride：移动步数
        
        1. padding：是否填充
        
    
    1. 输入输出的形状要求：
        
        1. input（bachsize,输入通道,输入高度,输入宽度）
        
        1. output（bachsize,输入通道,输入高度,输入宽度）
        
    
    1. 示例：
        
        ```Plain
        import torch
        import torchvision
        from torch import nn
        from torch.nn import Conv2d
        from torch.utils.data import DataLoader
        from torch.utils.tensorboard import SummaryWriter
        
        dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
        
        dataloader = DataLoader(dataset,batch_size=64)
        
        class Cool(nn.Module):
            def __init__(self):
                super(Cool,self).__init__()
                self.conv1 = Conv2d(in_channels=3,out_channels=6,kernel_size=3,stride=1,padding=0)
        
            def forward(self,x):
                x = self.conv1(x)
                return x
        
        cool_nn = Cool()
        # print(cool_nn) # Cool((conv1): Conv2d(3, 6, kernel_size=(3, 3), stride=(1, 1)))
        writer = SummaryWriter("logs")
        step = 0
        for data in dataloader:
            imgs,targets = data
        
            # 模型的输入和输出有要求：shape必须是[bach_size,channel,high,weight]
            print(imgs.shape) # 输入的shape：torch.Size([64, 3, 32, 32])
            output = cool_nn(imgs)
            print(output.shape) # 输出的shape：torch.Size([64, 6, 30, 30])  channel变为6，且tensor变小了
            writer.add_images("input",imgs,step)
            output = torch.reshape(output,(-1,3,30,30)) # 设置成-1会自动计算值
            writer.add_images("output", output,step)
            step = step + 1
        writer.close()
        ```
        
    
# **池化操作**
1. 什么是池化操作：
1. 池化操作示例：
    
    ```Plain
    import torch
    from torch import nn
    from torch.nn import MaxPool2d
    input = torch.tensor([[1,2,0,3,1],
                         [0,1,2,3,1],
                         [1,2,1,0,0],
                         [5,2,3,1,1],
                         [2,1,0,1,1]],dtype=torch.float32)
    input = torch.reshape(input,(-1,1,5,5))
    
    print(input.shape) # torch.Size([1, 1, 5, 5])
    
    class Cool(nn.Module):
    
        def __init__(self):
            super(Cool,self).__init__()
            self.maxpool1 = MaxPool2d(kernel_size=3,ceil_mode=False)
    
        def forward(self,input):
            output = self.maxpool1(input)
            return output
    
    cool = Cool()
    output = cool(input)
    print(output) # tensor([[[[2., 3.],[5., 1.]]]])
    
    # ceil_mode=False: tensor([[[[2.]]]])
    ```
    
1. torch.nn.MaxPool2d
    
    参数：
    
    1. **kernel_size** – the size of the window to take a max over
    
    1. **stride** – the stride of the window. Default value is `kernel_size`（默认步长是池化核的大小）
    
    1. **padding** – implicit zero padding to be added on both sides
    
    1. **dilation** – a parameter that controls the stride of elements in the window
    
    1. **return_indices** – if `True`, will return the max indices along with the outputs. Useful for [`torch.nn.MaxUnpool2d`](https://pytorch.org/docs/stable/generated/torch.nn.MaxUnpool2d.html#torch.nn.MaxUnpool2d) later
    
    1. **ceil_mode** – when True, will use ceil instead of floor to compute the output shape
    
1. 示例：
    
    ```Plain
    import torch
    import torchvision
    from torch import nn
    from torch.nn import MaxPool2d
    from torch.utils.data import DataLoader
    from torch.utils.tensorboard import SummaryWriter
    
    dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
    
    dataloader = DataLoader(dataset,batch_size=64)
    
    
    class Cool(nn.Module):
    
        def __init__(self):
            super(Cool,self).__init__()
            self.maxpool1 = MaxPool2d(kernel_size=3,ceil_mode=True)
    
        def forward(self,input):
            output = self.maxpool1(input)
            return output
    
    cool = Cool()
    
    writer = SummaryWriter("logs")
    step = 0
    for data in dataloader:
        imgs,targets = data
        writer.add_images("input",imgs,step)
    
        output = cool(imgs)
        writer.add_images("output",output,step)
        step = step + 1
    
    writer.close()
    ```
    
# **非线性激活函数**

> 为神经网络引入非线性特质
1. ReLU
    
    1. Parameters
        
        **inplace** – can optionally do the operation in-place. Default: `False` （函数结果是否覆盖输入）
        
    
    1. Shape:
        
        1. Input: (*)(∗), where *∗ means any number of dimensions.
        
        1. Output: (*)(∗), same shape as the input.
        
    
    1. 示例：
        
        ```Plain
        import torch
        from torch import nn
        from torch.nn import ReLU
        
        input = torch.tensor([[1,-0.5],
                              [-1,3]])
        input = torch.reshape(input,(-1,1,2,2))
        
        class Cool(nn.Module):
        
            def __init__(self) -> None:
                super(Cool,self).__init__()
                self.relu1 = ReLU()
        
            def forward(self,input):
                output = self.relu1(input)
                return output
        cool = Cool()
        output = cool(input)
        print(output)
        
        # tensor([[[[1., 0.],
        #           [0., 3.]]]])
        ```
        
    
1. Sigmoid
    
    1. 让模型对处于中间范围的输入数据更敏感
    
    1. Shape:
        
        1. Input: (*)(∗), where *∗ means any number of dimensions.
        
        1. Output: (*)(∗), same shape as the input.
        
    
    1. 示例：
        
        ```Plain
        import torch
        import torchvision
        from torch import nn
        from torch.nn import Sigmoid
        from torch.utils.data import DataLoader
        from torch.utils.tensorboard import SummaryWriter
        
        dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
        
        dataloader = DataLoader(dataset,batch_size=64)
        
        class Cool(nn.Module):
            def __init__(self):
                super(Cool,self).__init__()
                self.sigmoid1 = Sigmoid()
        
            def forward(self,input):
                output = self.sigmoid1(input)
                return output
        
        cool_nn = Cool()
        
        writer = SummaryWriter("logs")
        step = 0
        for data in dataloader:
            imgs,targets = data
            writer.add_images("input",imgs,step)
        
            output = cool_nn(imgs)
            writer.add_images("output",output,step)
            step = step + 1
        writer.close()
        ```
        
    
# **线性层**
```Plain
CLASS:
			torch.nn.Linear(in_features, out_features, bias=True, device=None, dtype=None)
```
1. 线性操作：
1. 参数
    
    1. **in_features** – size of each input sample （输入规模）
    
    1. **out_features** – size of each output sample （输出规模）
    
    1. **bias** – If set to `False`, the layer will not learn an additive bias. Default: `True` （偏置）
    
1. 示例
    
    ```Plain
    import torch
    import torchvision
    from torch import nn
    from torch.nn import Linear
    from torch.utils.data import DataLoader
    from torch.utils.tensorboard import SummaryWriter
    
    dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
    
    dataloader = DataLoader(dataset,batch_size=64)
    
    class Cool(nn.Module):
        def __init__(self):
            super(Cool,self).__init__()
            self.linear1 = Linear(196608,10)
    
        def forward(self,input):
            output = self.linear1(input)
            return output
    
    cool_nn = Cool()
    
    for data in dataloader:
        imgs,targets = data
        print(imgs.shape) # torch.Size([64, 3, 32, 32])
    
        # 将输入的 tensor 展开成一条线
        input = torch.reshape(imgs,(1,1,1,-1))
        print(input.shape) # torch.Size([1, 1, 1, 196608])
    
        # 使用模型将[1,196608]变为了[1, 10]
        output = cool_nn(input)
        print(output.shape) # torch.Size([1, 1, 1, 10])
    ```
    
# **CIFAR10 小模型**
1. 模型结构
1. 代码：
    
    > 输入输出的格式：
    > 
    > input（bachsize,输入通道,输入高度,输入宽度）
    > 
    > output（bachsize,输入通道,输入高度,输入宽度）
    > 
    > 卷积层中，要根据H_{in},kernel\_size,dilation,stride 计算 padding
    
    ```Plain
    import torch
    from torch import nn
    from torch.nn import Sequential, Conv2d, MaxPool2d, Flatten, Linear
    from torch.utils.tensorboard import SummaryWriter
    
    class Demo(nn.Module):
        def __init__(self) -> None:
            super(Demo,self).__init__()
            self.module1 = Sequential(
                Conv2d(3,32,5,padding=2),   # dilation默认等于1，stride = 1
                MaxPool2d(2),
                Conv2d(32,32,5,padding=2),
                MaxPool2d(2),
                Conv2d(32,64,5,padding=2),
                MaxPool2d(2),
                Flatten(),
                Linear(1024,64),
                Linear(64,10)
            )
        def forward(self,x):
            x = self.module1(x)
            return x
    
    demo = Demo()
    print(demo)
    # Demo(
    #   (module1): Sequential(
    #     (0): Conv2d(3, 32, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
    #     (1): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    #     (2): Conv2d(32, 32, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
    #     (3): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    #     (4): Conv2d(32, 64, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
    #     (5): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    #     (6): Flatten(start_dim=1, end_dim=-1)
    #     (7): Linear(in_features=1024, out_features=64, bias=True)
    #     (8): Linear(in_features=64, out_features=10, bias=True)
    #   )
    # )
    
    input = torch.ones((64,3,32,32))
    output = demo(input)
    print(output.shape)
    # torch.Size([64, 10])
    ```
    
1. 使用TensorBoard 查看模型
    
    ```Plain
    writer = SummaryWriter("logs")
    writer.add_graph(demo,input)
    writer.close()
    ```
    
# **损失函数**

> 目的：
> 
> 1. 计算实际输出与目标之间的差距
> 
> 1. 为我们更新输出提供一定的依据（反向传播），利用梯度优化权重
1. L1LOSS
    
    ```Plain
    CLASS
    	torch.nn.L1Loss(size_average=None, reduce=None, reduction='mean')
    ```
    
    1. 计算公式：
        
        $$l_n=|x_n-y_n|\\  
        L=\{l_1,l_2,...,l_N\}^T\\  
        \eta(x,y)=  
        \left\{  
        \begin{array}{lr}  
        mean(L),&reduction=mean\\  
        sum(L),&reduction=sum  
        \end{array}  
        \right.$$
        
    
    1. 示例：
        
        ```Plain
        import torch
        from torch import nn
        
        inputs = torch.tensor([1,2,3],dtype=torch.float32)
        targets = torch.tensor([1,2,5],dtype=torch.float32)
        
        inputs = torch.reshape(inputs,(1,1,1,3))
        targets = torch.reshape(targets,(1,1,1,3))
        
        loss_l1 = nn.L1Loss(reduction='mean')
        result_l1 = loss_l1(inputs,targets)
        print(result_l1) # tensor(0.6667)
        ```
        
        $$\frac{(1-1)+(2-2)+(5-3)}{3}=0.6667$$
        
    
1. MSELoss
    
    ```Plain
    CLASStorch.nn.MSELoss(size_average=None, reduce=None, reduction='mean')
    ```
    
    1. 计算公式：
        
        $$l_n=(x_n-y_n)^2\\  
        L=\{l_1,l_2,...,l_N\}^T\\  
        \eta(x,y)=  
        \left\{  
        \begin{array}{lr}  
        mean(L),&reduction='mean'\\  
        sum(L),&reduction='sum'  
        \end{array}  
        \right.$$
        
    
    1. 示例：
        
        ```Plain
        import torch
        from torch import nn
        
        inputs = torch.tensor([1,2,3],dtype=torch.float32)
        targets = torch.tensor([1,2,5],dtype=torch.float32)
        
        inputs = torch.reshape(inputs,(1,1,1,3))
        targets = torch.reshape(targets,(1,1,1,3))
        
        loss_mse = nn.MSELoss()
        result_mse = loss_mse(inputs,targets)
        print(result_mse) # tensor(1.3333)
        ```
        
        $$\frac{(1-1)^2+(2-2)^2+(5-3)^2}{3}=1.333$$
        
    
1. CrossEntropyLoss（交叉熵）
    
    ```Plain
    CLASS
    		torch.nn.CrossEntropyLoss(weight=None, size_average=None, ignore_index=- 100, reduce=None, reduction='mean', label_smoothing=0.0)
    ```
    
    1. 计算公式
        
        $$loss(x,class)=-x[class]+log(\sum_jexp(x[j]))$$
        
    
    1. 示例：
        
        1. 输入：dog的图像
        
        1. 分类：person, dog, cat { 0 1 2 }
        
        1. 输出：x=[0.1,0.2,0.3]
        
        1. target：class=1
        
        1. loss(x,class)= -0.2 +log(exp(0.1)+exp(0.2)+exp(0.3))
        
        > -x[class] 越大，即 x[1]越大，则 loss(x,class) 越小，表示结果越正确
        
        ```Plain
        inputs = torch.tensor([0.1,0.2,0.3])
        inputs = torch.reshape(inputs,(1,3))
        targets = torch.tensor([1])
        
        loss_CrossE = nn.CrossEntropyLoss()
        result_CrossE = loss_CrossE(inputs,targets)
        print(result_CrossE) # tensor(1.1019)
        ```
        
        $$-0.2+ln(e^{0.1}+e^{0.2}+e^{0.3})=1.1019$$
        
    
1. CrossEntropyLoss 在 网络中的应用
    
    ```Plain
    import torch
    import torchvision
    from torch import nn
    from torch.nn import Sequential, Conv2d, MaxPool2d, Flatten, Linear
    from torch.utils.data import DataLoader
    from torch.utils.tensorboard import SummaryWriter
    
    dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
    
    dataloader = DataLoader(dataset,batch_size=1)
    
    class Demo(nn.Module):
        def __init__(self) -> None:
            super(Demo,self).__init__()
            self.module1 = Sequential(
                Conv2d(3,32,5,padding=2),
                MaxPool2d(2),
                Conv2d(32,32,5,padding=2),
                MaxPool2d(2),
                Conv2d(32,64,5,padding=2),
                MaxPool2d(2),
                Flatten(),
                Linear(1024,64),
                Linear(64,10)
            )
        def forward(self,x):
            x = self.module1(x)
            return x
    
    demo = Demo()
    crossE_loss = nn.CrossEntropyLoss()
    for data in dataloader:
        imgs,targets = data
        # 放入模型
        outputs = demo(imgs)
        # 输出结果 (相当于 loss的x )
        print(outputs)  # tensor([[ 0.0181,  0.0197,  0.0802,  0.1444,  0.1809,  0.0876,  0.0950, -0.0652,
                        #          -0.0341,  0.0494]], grad_fn=<AddmmBackward0>)
        # 输出预期结果 (相当于 loss的class )
        print(targets)  # tensor([3])
    
        # 计算loss
        result_loss = crossE_loss(outputs,targets)
        print(result_loss)  # tensor(2.2184, grad_fn=<NllLossBackward0>)
    ```
    
# **反向传播**
```Plain
import torch
import torchvision
from torch import nn
from torch.nn import Sequential, Conv2d, MaxPool2d, Flatten, Linear
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
dataloader = DataLoader(dataset,batch_size=1)
class Demo(nn.Module):
    def __init__(self) -> None:
        super(Demo,self).__init__()
        self.module1 = Sequential(
            Conv2d(3,32,5,padding=2),
            MaxPool2d(2),
            Conv2d(32,32,5,padding=2),
            MaxPool2d(2),
            Conv2d(32,64,5,padding=2),
            MaxPool2d(2),
            Flatten(),
            Linear(1024,64),
            Linear(64,10)
        )
    def forward(self,x):
        x = self.module1(x)
        return x
demo = Demo()
crossE_loss = nn.CrossEntropyLoss()
for data in dataloader:
    imgs,targets = data
    # 放入模型
    outputs = demo(imgs)
    # 输出结果 (相当于 loss的x )
    print(outputs)  # tensor([[ 0.0181,  0.0197,  0.0802,  0.1444,  0.1809,  0.0876,  0.0950, -0.0652,
                    #          -0.0341,  0.0494]], grad_fn=<AddmmBackward0>)
    # 输出预期结果 (相当于 loss的class )
    print(targets)  # tensor([3])
    # 计算loss
    result_loss = crossE_loss(outputs,targets)
    print(result_loss)  # tensor(2.2184, grad_fn=<NllLossBackward0>)
    result_loss.backward()
```
没执行`result_loss.backward()`前
执行`result_loss.backward()`后
# **优化器**
1. torch.optim是一个实现各种优化算法的包
1. 要使用torch.optim，必须构造一个优化器对象，该对象将保存当前状态并根据计算出的梯度更新参数
1. 构建一个优化器：
    
    ```Plain
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    optimizer = optim.Adam([var1, var2], lr=0.0001)
    ```
    
1. 参数：
    
    1. params ( iterable ) – 要优化的参数的迭代或定义参数组的字典，这个参数是必须的
    
    1. lr：学习率
        
        ```Plain
        # 想要指定每层学习率时
        optim.SGD([
                        {'params': model.base.parameters()},
                        {'params': model.classifier.parameters(), 'lr': 1e-3}
                    ], lr=1e-2, momentum=0.9)
        ```
        
        意味着model.base的参数将使用 的默认学习率`1e-2`， model.classifier的参数将使用 的学习率`1e-3`
        
        `0.9`是所有参数将使用动量
        
    
1. 采取优化的步骤
    
    1. 大多数优化器支持的简化版本
        
        ```Plain
        for input, target in dataset:
        
            # 将优化器中的梯度清零
            optimizer.zero_grad()
        
            output = model(input)
        
            # 计算损失函数值
            loss = loss_fn(output, target)
        
            # loss反向传播
            loss.backward()
        
            # 所有优化器都实现了一个step()更新参数的方法
            optimizer.step()
        ```
        
    
    1. 某些优化算法（例如共轭梯度和 LBFGS）需要多次重新评估函数，因此您必须传入一个闭包，以便它们重新计算模型。闭包应该清除梯度，计算损失并返回它
        
        ```Plain
        for input, target in dataset:
            def closure():
                optimizer.zero_grad()
                output = model(input)
                loss = loss_fn(output, target)
                loss.backward()
                return loss
            optimizer.step(closure)
        ```
        
    
1. 随机梯度优化 SGD 的使用示例：
    
    ```Plain
    import torch
    import torchvision
    from torch import nn
    from torch.nn import Sequential, Conv2d, MaxPool2d, Flatten, Linear
    from torch.utils.data import DataLoader
    from torch.utils.tensorboard import SummaryWriter
    
    dataset = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
    
    dataloader = DataLoader(dataset,batch_size=1)
    
    class Demo(nn.Module):
        def __init__(self) -> None:
            super(Demo,self).__init__()
            self.module1 = Sequential(
                Conv2d(3,32,5,padding=2),
                MaxPool2d(2),
                Conv2d(32,32,5,padding=2),
                MaxPool2d(2),
                Conv2d(32,64,5,padding=2),
                MaxPool2d(2),
                Flatten(),
                Linear(1024,64),
                Linear(64,10)
            )
        def forward(self,x):
            x = self.module1(x)
            return x
    
    demo = Demo()
    crossE_loss = nn.CrossEntropyLoss()
    
    # 创建优化器对象
    optim = torch.optim.SGD(demo.module1.parameters(),lr=0.01)
    for epoch in range(20):
        curr_loss = 0.0
        for data in dataloader:
            imgs,targets = data
            outputs = demo(imgs)
            # 计算 loss
            result_loss = crossE_loss(outputs,targets)
    
            # 对优化器内的参数清零
            optim.zero_grad()
    
            # loss 反向传播
            result_loss.backward()
            #
            optim.step()
    
            # 计算每一个 epoch 的 loss 总和
            curr_loss = curr_loss + result_loss
        print(curr_loss)
    
        # tensor(18745.0117, grad_fn= < AddBackward0 >)
        # tensor(16230.8096, grad_fn= < AddBackward0 >)
        # tensor(15569.7373, grad_fn= < AddBackward0 >)
        # ...
        # loss 值在优化器的作用下不断下降
    ```
    
    1. 执行 result_loss.backward() 之前
    
    1. 执行 result_loss.backward() 之后
    
    1. 执行 optim.step() 之后
    
# **使用现成的模型**
1. 下载模型
    
    ```Plain
    import torchvision
    from torch import nn
    
    vgg16_false = torchvision.models.vgg16(pretrained=False)
    vgg16_true = torchvision.models.vgg16(pretrained=True)
    
    # pretrained 为 True 表示将别人预训练好的参数也下载下来
    # 					  为 False 表示只下载模型的框架
    
    print(vgg16_true)
    ```
    
    ```Plain
    VGG(
      (features): Sequential(
        (0): Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (1): ReLU(inplace=True)
        (2): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (3): ReLU(inplace=True)
        (4): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
        (5): Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (6): ReLU(inplace=True)
        (7): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (8): ReLU(inplace=True)
        (9): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
        (10): Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (11): ReLU(inplace=True)
        (12): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (13): ReLU(inplace=True)
        (14): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (15): ReLU(inplace=True)
        (16): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
        (17): Conv2d(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (18): ReLU(inplace=True)
        (19): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (20): ReLU(inplace=True)
        (21): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (22): ReLU(inplace=True)
        (23): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
        (24): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (25): ReLU(inplace=True)
        (26): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (27): ReLU(inplace=True)
        (28): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (29): ReLU(inplace=True)
        (30): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
      )
      (avgpool): AdaptiveAvgPool2d(output_size=(7, 7))
      (classifier): Sequential(
        (0): Linear(in_features=25088, out_features=4096, bias=True)
        (1): ReLU(inplace=True)
        (2): Dropout(p=0.5, inplace=False)
        (3): Linear(in_features=4096, out_features=4096, bias=True)
        (4): ReLU(inplace=True)
        (5): Dropout(p=0.5, inplace=False)
        (6): Linear(in_features=4096, out_features=1000, bias=True)
      )
    )
    ```
    
1. 自定义网络：
    
    > 之前的 CIFAR10是一个10分类的数据集，但vgg16是一个 1000分类的模型
    > 
    > 如何修改模型，让模型也变为 10 分类？
    
    1. 在网络的添加一层
        
        ```Plain
        import torchvision
        from torch import nn
        
        vgg16_false = torchvision.models.vgg16(pretrained=False)
        vgg16_true = torchvision.models.vgg16(pretrained=True)
        
        # 添加一个 1000 -> 10 的线性层
        
        vgg16_true.classifier.add_module("add_linear",nn.Linear(1000,10))
        print(vgg16_true)
        ```
        
        ```Plain
        # (classifier): Sequential(
        #     (0): Linear(in_features=25088, out_features=4096, bias=True)
        # 		 (1): ReLU(inplace=True)
        # 		 (2): Dropout(p=0.5, inplace=False)
        # 		 (3): Linear(in_features=4096, out_features=4096, bias=True)
        # 		 (4): ReLU(inplace=True)
        # 		 (5): Dropout(p=0.5, inplace=False)
        # 		 (6): Linear(in_features=4096, out_features=1000, bias=True)
        # 		 (add_linear): Linear(in_features=1000, out_features=10, bias=True)
        # )
        ```
        
    
    1. 修改网络中的某一层
        
        ```Plain
        import torchvision
        from torch import nn
        
        vgg16_false = torchvision.models.vgg16(pretrained=False)
        vgg16_true = torchvision.models.vgg16(pretrained=True)
        
        # 将 classifier 的第6层 修改成想要的
        vgg16_true.classifier[6] = nn.Linear(4096,10)
        print(vgg16_true)
        ```
        
        ```Plain
        #(classifier): Sequential(
        #    (0): Linear(in_features=25088, out_features=4096, bias=True)
        #    (1): ReLU(inplace=True)
        #    (2): Dropout(p=0.5, inplace=False)
        #    (3): Linear(in_features=4096, out_features=4096, bias=True)
        #    (4): ReLU(inplace=True)
        #    (5): Dropout(p=0.5, inplace=False)
        #    (6): Linear(in_features=4096, out_features=10, bias=True)
        #  )
        ```
        
    
# **模型的保存与加载**
1. 保存与加载的方式一：保存 模型的 框架 + 参数
    
    ```Plain
    import torch
    import torchvision
    
    vgg16 = torchvision.models.vgg16(pretrained=False)
    
    torch.save(vgg16,"vgg16_method1.pth")
    ```
    
    ```Plain
    import torch
    import torchvision
    
    model_1= torch.load("vgg16_method1.pth")
    print(model_1)
    #
    # VGG(
    #   (features): Sequential(
    #    ...
    #   )
    #   (avgpool): AdaptiveAvgPool2d(output_size=(7, 7))
    #   (classifier): Sequential(
    #     (0): Linear(in_features=25088, out_features=4096, bias=True)
    #     ...
    #     (6): Linear(in_features=4096, out_features=1000, bias=True)
    #   )
    # )
    ```
    
1. **（推荐）**保存与加载的方式二：保存 模型的 参数（字典）
    
    ```Plain
    import torch
    import torchvision
    from torch import nn
    
    vgg16 = torchvision.models.vgg16(pretrained=False)
    
    torch.save(vgg16.state_dict(),"vgg16_method2.pth")
    ```
    
    ```Plain
    import torch
    import torchvision
    
    model_2 = torch.load("vgg16_method2.pth")
    print(model_2)
    # OrderedDict([('features.0.weight', tensor([[[[-0.0387, -0.0751, -0.0295],
    #           [ 0.1210,  0.0214,  0.0127],
    #           [-0.0075,  0.0164, -0.0065]],
    #
    #          [[ 0.0043, -0.0143,  0.0618],
    #           [-0.0032, -0.0154,  0.0711],
    #           [ 0.0121,  0.0336, -0.0187]],
    #
    #          [[ 0.0856,  0.0190,  0.0393],
    #           [ 0.0478, -0.0604,  0.0951],
    #           [-0.0239, -0.0242, -0.0718]]],
    ```
    
    方式二只会 按字典形式保存模型的参数，如何加载成完整的模型？
    
    ```Plain
    # 先下载模型框架
    model_2 = torchvision.models.vgg16(pretrained=False)
    # 向模型框架中加载
    model_2.load_state_dict(torch.load("vgg16_method2.pth"))
    print(model_2)
    #
    # VGG(
    #   (features): Sequential(
    #    ...
    #   )
    #   (avgpool): AdaptiveAvgPool2d(output_size=(7, 7))
    #   (classifier): Sequential(
    #     (0): Linear(in_features=25088, out_features=4096, bias=True)
    #     ...
    #     (6): Linear(in_features=4096, out_features=1000, bias=True)
    #   )
    # )
    ```
    
1. 如果是保存加载自己写的模型需要将模型的那个文件的所有模块都引入
    
    ```Plain
    # 例如
    from nn_loss_network import *
    
    # 否则加载模型会报错
    ```
    
# **完整的模型训练**
```Plain
import torchvision
import torch
from torch.utils.tensorboard import SummaryWriter
from model import *
from torch.utils.data import DataLoader
train_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
test_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
train_set_size = len(train_set)
test_set_size = len(test_set)
print("训练数据集的长度为：{}".format(train_set_size))
print("测试数据集的长度为：{}".format(test_set_size))
train_loader = DataLoader(dataset=test_set,batch_size=64)
test_loader = DataLoader(dataset=test_set,batch_size=64)
# 创建网络模型
demo_module = Demo()
# 定义损失函数
loss_fn = nn.CrossEntropyLoss()
# 定义优化器
lerning_rate = 0.01
optimizer = torch.optim.SGD(demo_module.parameters(),lr=lerning_rate)
# 设置训练网络的参数
# 记录训练的次数
total_train_step = 0
# 记录测试的次数
total_test_step = 0
# 训练的轮数
epoch = 10
# 添加tensorboard
writer = SummaryWriter("./logs")
for i in range(epoch):
    print("-------第{}轮训练开始--------".format(i+1))
    # 训练步骤开始
    for data in train_loader:
        imgs,targets = data
        output = demo_module(imgs)
        loss = loss_fn(output,targets)
        # 优化器优化模型
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_train_step = total_train_step + 1
        # 分阶段打印结果
        if total_train_step % 100 ==0:
            print("训练次数：{}，Loss：{}".format(total_train_step,loss.item()))
            writer.add_scalar("train_loss",loss.item(),total_train_step)
    # 测试步骤开始
    total_test_loss = 0
    total_accuracy = 0
    with torch.no_grad(): # 取消梯度，确保测试时不会对模型进行调优
        for data in test_loader:
            imgs,targets = data
            output = demo_module(imgs)
            # 测试时不需要反向传播和优化器
            loss = loss_fn(output,targets)
            total_test_loss = total_test_loss + loss
            # 计算当前output中的分类正确的个数
            # argmax(1)：按行取max
            accuracy = (output.argmax(1) == targets).sum()
            # 分类正确的个数累加
            total_accuracy =  total_accuracy + accuracy
    print("整体测试集上的loss：{}".format(total_test_loss))
    print("整体测试集上的正确率：{}".format(total_accuracy/test_set_size))
    writer.add_scalar("test_loss",total_test_loss,total_test_step)
    writer.add_scalar("test_accuray",total_accuracy/test_set_size,total_test_step)
    total_test_step = total_test_step + 1
    # 保存模型
    torch.save(demo_module,"demo_{}.pth".format(i))
writer.close()
```
```Plain
训练数据集的长度为：10000
测试数据集的长度为：10000
-------第1轮训练开始--------
训练次数：100，Loss：2.2933249473571777
整体测试集上的loss：359.2919616699219
整体测试集上的正确率：0.12600000202655792
-------第2轮训练开始--------
训练次数：200，Loss：2.269317626953125
训练次数：300，Loss：2.2691822052001953
整体测试集上的loss：354.2793884277344
整体测试集上的正确率：0.1370999962091446
-------第3轮训练开始--------
训练次数：400，Loss：2.2112622261047363
整体测试集上的loss：342.08428955078125
整体测试集上的正确率：0.156700000166893
-------第4轮训练开始--------
训练次数：500，Loss：2.080399513244629
训练次数：600，Loss：1.9836218357086182
整体测试集上的loss：343.74505615234375
整体测试集上的正确率：0.1996999979019165
-------第5轮训练开始--------
训练次数：700，Loss：2.0485446453094482
整体测试集上的loss：332.7223815917969
整体测试集上的正确率：0.2425999939441681
-------第6轮训练开始--------
训练次数：800，Loss：1.9634602069854736
训练次数：900，Loss：1.852600336074829
整体测试集上的loss：318.44708251953125
整体测试集上的正确率：0.2816999852657318
-------第7轮训练开始--------
训练次数：1000，Loss：1.8015007972717285
整体测试集上的loss：305.01171875
整体测试集上的正确率：0.31679999828338623
-------第8轮训练开始--------
训练次数：1100，Loss：1.873431921005249
训练次数：1200，Loss：1.9950140714645386
整体测试集上的loss：293.81182861328125
整体测试集上的正确率：0.33869999647140503
-------第9轮训练开始--------
训练次数：1300，Loss：1.7503139972686768
训练次数：1400，Loss：1.6164969205856323
整体测试集上的loss：285.78564453125
整体测试集上的正确率：0.3569999933242798
-------第10轮训练开始--------
训练次数：1500，Loss：1.6842454671859741
整体测试集上的loss：279.0702209472656
整体测试集上的正确率：0.375
```
# **使用 GPU 训练 1**
1. 使用位置：
    
    1. 网络模型
    
    1. 数据（输入（imgs）、标注（targets））
    
    1. 损失函数
    
1. 示例：
    
    ```Plain
    if torch.cuda.is_available():
        demo_module.cuda()
    ```
    
    ```Python
    import torchvision
    import torch
    from torch.utils.tensorboard import SummaryWriter
    
    from model import *
    
    from torch.utils.data import DataLoader
    train_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
    test_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
    
    train_set_size = len(train_set)
    test_set_size = len(test_set)
    
    print("训练数据集的长度为：{}".format(train_set_size))
    print("测试数据集的长度为：{}".format(test_set_size))
    
    train_loader = DataLoader(dataset=test_set,batch_size=64)
    test_loader = DataLoader(dataset=test_set,batch_size=64)
    
    # 创建网络模型
    demo_module = Demo()
    if torch.cuda.is_available():
        demo_module.cuda()
    # 定义损失函数
    loss_fn = nn.CrossEntropyLoss()
    if torch.cuda.is_available():
        loss_fn = loss_fn.cuda()
    
    # 定义优化器
    lerning_rate = 0.01
    optimizer = torch.optim.SGD(demo_module.parameters(),lr=lerning_rate)
    
    # 设置训练网络的参数
    # 记录训练的次数
    total_train_step = 0
    # 记录测试的次数
    total_test_step = 0
    # 训练的轮数
    epoch = 10
    
    # 添加tensorboard
    writer = SummaryWriter("./logs")
    for i in range(epoch):
        print("-------第{}轮训练开始--------".format(i+1))
    
        # 训练步骤开始
        for data in train_loader:
            imgs,targets = data
            if torch.cuda.is_available():
                imgs = imgs.cuda()
                targets = targets.cuda()
    
            output = demo_module(imgs)
            loss = loss_fn(output,targets)
    
            # 优化器优化模型
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
            total_train_step = total_train_step + 1
            # 分阶段打印结果
            if total_train_step % 100 ==0:
                print("训练次数：{}，Loss：{}".format(total_train_step,loss.item()))
                writer.add_scalar("train_loss",loss.item(),total_train_step)
    
        # 测试步骤开始
        total_test_loss = 0
        total_accuracy = 0
    
        with torch.no_grad(): # 取消梯度，确保测试时不会对模型进行调优
            for data in test_loader:
                imgs,targets = data
                if torch.cuda.is_available():
                    imgs = imgs.cuda()
                    targets = targets.cuda()
    
                output = demo_module(imgs)
    
                # 测试时不需要反向传播和优化器
                loss = loss_fn(output,targets)
                total_test_loss = total_test_loss + loss
    
                # 计算当前output中的分类正确的个数
                # argmax(1)：按行取max
                accuracy = (output.argmax(1) == targets).sum()
                # 分类正确的个数累加
                total_accuracy =  total_accuracy + accuracy
    
        print("整体测试集上的loss：{}".format(total_test_loss))
        print("整体测试集上的正确率：{}".format(total_accuracy/test_set_size))
        writer.add_scalar("test_loss",total_test_loss,total_test_step)
        writer.add_scalar("test_accuray",total_accuracy/test_set_size,total_test_step)
    
        total_test_step = total_test_step + 1
    
        # 保存模型
        torch.save(demo_module,"demo_{}.pth".format(i))
    
    writer.close()
    ```
    
    ```Plain
    (pytorch_one) C:\Users\lenovo\PycharmProjects\pytorch_demo>nvidia-smi
    Wed Nov 24 20:36:44 2021
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 496.49       Driver Version: 496.49       CUDA Version: 11.5     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name            TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |                               |                      |               MIG M. |
    |===============================+======================+======================|
    |   0  NVIDIA GeForce ... WDDM  | 00000000:01:00.0 Off |                  N/A |
    | N/A    0C    P8    N/A /  N/A |     40MiB /  4096MiB |      1%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+
    
    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
    |        ID   ID                                                   Usage      |
    |=============================================================================|
    |  No running processes found                                                 |
    +-----------------------------------------------------------------------------+
    ```
    
# **使用 GPU 训练 2**
```Plain
import torchvision
import torch
from torch.utils.tensorboard import SummaryWriter
from model import *
from torch.utils.data import DataLoader
train_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
test_set = torchvision.datasets.CIFAR10("./dataset",train=False,transform=torchvision.transforms.ToTensor(),download=True)
train_set_size = len(train_set)
test_set_size = len(test_set)
print("训练数据集的长度为：{}".format(train_set_size))
print("测试数据集的长度为：{}".format(test_set_size))
train_loader = DataLoader(dataset=test_set,batch_size=64)
test_loader = DataLoader(dataset=test_set,batch_size=64)
# 定义训练的设备
device = torch.device("cuda:0")
# 创建网络模型
demo_module = Demo()
demo_module = demo_module.to(device)
# 定义损失函数
loss_fn = nn.CrossEntropyLoss()
loss_fn = loss_fn.to(device)
# 定义优化器
lerning_rate = 0.01
optimizer = torch.optim.SGD(demo_module.parameters(),lr=lerning_rate)
# 设置训练网络的参数
# 记录训练的次数
total_train_step = 0
# 记录测试的次数
total_test_step = 0
# 训练的轮数
epoch = 10
# 添加tensorboard
writer = SummaryWriter("./logs")
for i in range(epoch):
    print("-------第{}轮训练开始--------".format(i+1))
    # 训练步骤开始
    for data in train_loader:
        imgs,targets = data
        imgs = imgs.to(device)
        targets = targets.to(device)
        output = demo_module(imgs)
        loss = loss_fn(output,targets)
        # 优化器优化模型
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_train_step = total_train_step + 1
        # 分阶段打印结果
        if total_train_step % 100 ==0:
            print("训练次数：{}，Loss：{}".format(total_train_step,loss.item()))
            writer.add_scalar("train_loss",loss.item(),total_train_step)
    # 测试步骤开始
    total_test_loss = 0
    total_accuracy = 0
    with torch.no_grad(): # 取消梯度，确保测试时不会对模型进行调优
        for data in test_loader:
            imgs,targets = data
            imgs = imgs.to(device)
            targets = targets.to(device)
            output = demo_module(imgs)
            # 测试时不需要反向传播和优化器
            loss = loss_fn(output,targets)
            total_test_loss = total_test_loss + loss
            # 计算当前output中的分类正确的个数
            # argmax(1)：按行取max
            accuracy = (output.argmax(1) == targets).sum()
            # 分类正确的个数累加
            total_accuracy =  total_accuracy + accuracy
    print("整体测试集上的loss：{}".format(total_test_loss))
    print("整体测试集上的正确率：{}".format(total_accuracy/test_set_size))
    writer.add_scalar("test_loss",total_test_loss,total_test_step)
    writer.add_scalar("test_accuray",total_accuracy/test_set_size,total_test_step)
    total_test_step = total_test_step + 1
    # 保存模型
    torch.save(demo_module,"demo_{}.pth".format(i))
writer.close()
```
# **分类测试**
网上找一张图片
```Plain
zxxxxxxxxxx30 1import torch2import torchvision3from PIL import Image4from torch import nn56# 要测试的图片7image_path = "211716.jpg"8image = Image.open(image_path)910transform = torchvision.transforms.Compose([torchvision.transforms.Resize((32,32)),torchvision.transforms.ToTensor()])1112image = transform(image)13print(image.shape)  # torch.Size([3, 32, 32])1415# model = torch.load("vgg16_method1.pth")16# 如果时在GPU上训练出来的模型，想要在CPU上跑，使用 map_location17model = torch.load("demo_29.pth",map_location=torch.device('cpu'))1819image = torch.reshape(image,(-1,3,32,32))2021model.eval()22with torch.no_grad():23    output = model(image)24print(output)25# tensor([[-3.2157, -0.8506,  0.1544,  2.8471, -2.3946,  2.9677,  1.5716,  0.1426,26#          -2.2489,  0.2320]])2728print(output.argmax(1))     # tensor([5])2930# 分类成功！
```