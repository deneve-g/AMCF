var importJs=document.createElement('script')
importJs.setAttribute("type","text/javascript")
importJs.setAttribute("src", 'https://ajax.microsoft.com/ajax/jquery/jquery-3.5.1.min.js')
document.getElementsByTagName("head")[0].appendChild(importJs)

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

function setNativeValue(element, value) {
  const valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
  const prototype = Object.getPrototypeOf(element);
  const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
  
  if (valueSetter && valueSetter !== prototypeValueSetter) {
  	prototypeValueSetter.call(element, value);
  } else {
    valueSetter.call(element, value);
  }
}

async function text_2_image(texts){
  for(var i = 0; i < texts.length; i++){
    console.log(texts[i])
    var input_ele = document.getElementsByClassName("ant-input")[0]
    var create_btn = document.getElementsByTagName('button')[0]
    var now_image_length = $("div[class^=historyItem]").length
    setNativeValue(input_ele, texts[i])
    input_ele.dispatchEvent(new Event('input', { bubbles: true }));
    create_btn.click()
    while($("div[class^=historyItem]").length == now_image_length){
      await sleep(5000)
      console.log('wait...')
    }
    var imgs_href = []
    while(imgs_href.length == 0){
      var imgs = $("div[class^=historyItem]:first .rc-image a")
      for(var j = 0; j < imgs.length; j++){
        if(imgs[j].href){
          if(global_imgs_href[0].indexOf(imgs[j].href) >= 0){
            break
          }
          console.log(imgs[j].href)
          imgs_href.push(imgs[j].href)
          // imgs[j].click()
          await sleep(2000)
        }
      }
      if(imgs_href.length){
        global_imgs_href.unshift(imgs_href)
      }else{
        await sleep(5000)
        console.log('wait...')
      }
    }
    await sleep(2000)
    console.log('success')
  }
  console.log(global_imgs_href)
}

var texts=['a young girl sits in front of a computer holding a phone. ']
var global_imgs_href = [['']]
text_2_image(texts)

// console.log(global_imgs_href)
// 362num_14relation_re12_test_imageid

