import pywebio
import nibabel
import io
import time
from matplotlib import pyplot as plt
import PIL.Image

import torch

import random
def generate_random_str(target_length=32):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(target_length):
        random_str += base_str[random.randint(0, length)]
    return random_str


def print_logs(content, user_ip):
    with open("./run_logs/" + user_ip+"run_logs.csv", 'a') as file:
        file.write(str(pywebio.session.info.user_ip) + "," +
                   str(pywebio.session.info.user_agent.device.model) + "," +
                   str(pywebio.session.info.user_agent.browser.family) + "," + time.ctime() + ",")
        file.write(content)
        

def zlzheimer_diagnostic_system(is_demo=False):
    """
    基于 PyWebIO 和 PyTorch 的阿尔兹海默智能诊断系统
    """
    def show_img(img): 
        """
        接收二进制图像，用于展示图像
        """
        pywebio.output.popup("加载中", [  
                pywebio.output.put_loading(), 
        ])
        pywebio.output.popup("上传的图像",[ 
            pywebio.output.put_image(img), 
        ])

    user_ip = str(pywebio.session.info.user_ip)+generate_random_str(16)
    from pyecharts.charts import Bar

    def draw_chart(x_label,data):
        """
        输入 x 轴标签和数据列表，返回图表的 HTML 文本
        """
        chart = (
            Bar()
            .add_xaxis(x_label) # 设置 x 轴标签列表
            .add_yaxis("output_value", data) # 传入数据列表和标签
            .set_global_opts(title_opts={"text": "模型输出", "subtext": ""},) # text 的值为图表标题
        )
        return chart.render_notebook() # 返回图表对象的 html 文本

    while 1:
        pywebio.output.clear()
        pywebio.output.put_warning("识别结果仅供参考", closable=True, position=- 1)
        pywebio.output.put_markdown("<h1><center>基于PyWebIO 和 PyTorch 的阿尔兹海默智能诊断系统</center></h1><hr>")
        pywebio.output.put_row([
            pywebio.output.put_button('使用示例图像',
                                      onclick=lambda: zlzheimer_diagnostic_system(is_demo=True), disabled=is_demo),
            pywebio.output.put_link(name="模型Github仓库", url="https://github.com/JavaSsun/SE-DenseNet-for-Alzheimer"),
            pywebio.output.put_link(name="系统Github仓库", url="https://github.com/JavaSsun/AD_Intelligent_Diagnosis"),
            pywebio.output.put_link(name="演示数据集", url="https://github.com/JavaSsun/AD_Test_Data"),
        ])
        net_img = PIL.Image.open("./img/net_graph.png")
        brain_img = PIL.Image.open("./img/brain_demo1.png")
        
        pywebio.output.put_row(
            [pywebio.output.put_collapse("AI诊断流程", [pywebio.output.put_image(net_img)], open=True),
             pywebio.output.put_collapse("示例影像", [pywebio.output.put_image(brain_img)],open=True),
            ]
        )
        
        f = open("model_show.py", "r", encoding="UTF-8")
        code = f.read()
        f.close()
        pywebio.output.put_collapse("模型代码", [pywebio.output.put_code(code, "python")], open=False, position=- 1)
        pywebio.output.put_markdown("Ref: https://github.com/moboehle/Pytorch-LRP")
        pywebio.output.put_markdown("Datasets: https://adni.loni.usc.edu")
 
        nii_path = "./demodata/demo.nii"
        if not is_demo:
            pywebio.input.actions("", [{'label': "上传医学影像(.nii)", 'value': "上传医学影像(.nii)", 'color': 'success', }])
            input_img = pywebio.input.file_upload(label="上传医学影像(.nii)", accept=[".nii"], required=True)
            pywebio.output.popup("AI识别中", [
                pywebio.output.put_loading(),
            ])
            input_img = io.BytesIO(input_img['content'])
            nii_path = "./uploaded_img/" + generate_random_str() + ".nii"
            with open(nii_path, 'wb') as file:
                file.write(input_img.getvalue())  # 保存到本地
            print_logs("upload_file," + nii_path + ",\n", user_ip)

        if is_demo:
            pywebio.output.popup("加载中", [
                pywebio.output.put_loading(),
            ])
            is_demo = False

        img = nibabel.load(nii_path)
        img = img.get_fdata()
        print(img.shape)
        # (166, 256, 256, 1)

        torch.no_grad()
        test_model = torch.load("./model_save/myModel_109.pth", map_location=torch.device('cpu'))
        test_model.eval()

        processed_img = torch.from_numpy(img)
        processed_img = processed_img.squeeze()
        processed_img = processed_img.reshape(1, -1, 256, 256)
        processed_img = processed_img[:, 0:160, :, :].float()
        processed_img = processed_img.reshape((1, 1, -1, 256, 256))

        output = None
        with torch.no_grad():
            output = test_model(processed_img)
        ans_y = output.squeeze().tolist()
        print(ans_y)
        del test_model,processed_img

        from datasets import LABEL_LIST
        if min(ans_y) < 0:
            m = min(ans_y)
            for i in range(len(ans_y)):
                ans_y[i] -= 1.2 * m
        chart_html = draw_chart(LABEL_LIST, ans_y)
        pywebio.output.put_html(chart_html)

        ans = LABEL_LIST[output.argmax(1).item()]
        if ans == 'AD':
            ans += '（阿尔茨海默病）'
        elif ans == 'CN':
            ans += '（认知正常）'
        elif ans == 'MCI':
            ans += '（轻度认知障碍）'
        elif ans == 'EMCI':
            ans += '（早期轻度认知障碍）'
        elif ans == 'LMCI':
            ans += '（晚期轻度认知障碍）'
        show_result = [pywebio.output.put_markdown("诊断为：\n # " + ans),
                       pywebio.output.put_warning('结果仅供参考'),]
        pywebio.output.popup(title='AI识别结果', content=show_result)
        
       
        

        while 1:
            act = pywebio.input.actions(' ', ['查看图像', '上传新图像'], )
            if act == '上传新图像':
                pywebio.output.clear()
                break
            dim = pywebio.input.radio(label='查看视角', options=[('X',0,True), ('Y',1,False), ('Z',2,False)],
                                      required=True, inline=True)
            max_index = 0
            print(dim)
            if dim == 0:
                max_index = img.shape[0]
            if dim == 1:
                max_index = img.shape[1]
            if dim == 2:
                max_index = img.shape[2]
            index = pywebio.input.slider("查看层数", max_value=max_index - 1, step=1, value=100)

            if img.ndim == 4:
                if dim == 0:
                    plt.imshow(img[index+1, :, :, :], cmap='gray')
                if dim == 1:
                    plt.imshow(img[:, index+1, :, :], cmap='gray')
                if dim == 2:
                    plt.imshow(img[:, :, index+1, :], cmap='gray')

            if img.ndim == 3:
                if dim == 0:
                    plt.imshow(img[index, :, :], cmap='gray')
                elif dim == 1:
                    plt.imshow(img[:, index, :], cmap='gray')
                elif dim == 2:
                    plt.imshow(img[:, :, index], cmap='gray')

            plt.axis('off')
            png_path = './uploaded_img/' + generate_random_str() + '.png'
            plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
            show_img(PIL.Image.open(png_path))
            
            


if __name__ == "__main__":
    pywebio.platform.start_server(
        applications=[zlzheimer_diagnostic_system, ], # applications 参数为一个可迭代对象（此处是列表），里面放要运行的主函数。
        auto_open_webbrowser=False, # 不自动打开浏览器
        cdn=False, # 不使用 cdn
        debug=True, # 可以看到报错
        port=6008  # 运行在 6006 端口
    )
    # start_server 函数启动一个 http 服务器

