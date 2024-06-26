MMEvaluation 
====================================

### 1. Generate the images:

`python stablediffusion.py --model_name stable_diffusion_xl_base --file_name <path to original json file> --save_filename <path to save the images>`

### 2.Evaluate the generated images:


**2.1 use FID to evaluate the generated images by ground truth images, you should first download the coco2017 dataset and put it to /home/data/coco/:**

   `python ./evaluation/FID.py 
   --path <path to generated file>`

**2.2 use inception_score to evaluate the generated images:**

`python ./evaluation/inception_score.py --images_folder <path to generated images>`

if your images is saved to /dataset/geretaed_images, then you should run the command like this:
python ./evaluation/inception_score.py --images_folder /dataset/

**2.3 use yolov5 to detect the objects:**

`python ./yolov5_new/detect.py --weights ./yolov5_new/runs/train/exp31/weights/best.pt --source ./coco2017testdata/361_14relation_re12_test_imageid/generated_images  --data vrd.yaml  --device 0 --project ./coco2017testdata/361_14relation_re12_test_imageid`

then the file detect.json, new_detect.json and new_detect_filter.json will be generated, and run the command to caculate the accuracy:

`python ./yolov5_new/bbox_json_maker.py --files_path ./coco2017testdata/361_14relation_re12_test_imageid`

bbox_json_maker.py will filter the jsonfile by delete the images which have only one entity or no entity. So the final jsonfile is new_detect.json, new_detect_filter.json is only provided for next step.

**2.4 use the json file generated by step 2.3 to evaluate the relationship between each objects**

`cd rvlbert`

`python ./vrd/test.py --sum 574 --split test --gpus 0 --path ./coco2017testdata/361_14relation_re12_test_imageid`

the sum is needed because we want to caculate the accuracy of the whole dataset including the images which have only one entity or no entity.

* tips:rvlbert project need to run ./script/init.sh to construct the environment.

**2.5 use the neural-Image-assessment to assess the Aesthetic score of the generated images:**

`python ./neural-Image-assessment/test1.py --root_path ./coco2017testdata/361_14relation_re12_test_imageid --model_path ./ckpts/epoch-113.pth `

then the Aesthetic.json will be generated which record the Aesthetic score of each image including mean and std.

`python ./evaluation/Aesthetics.py` to generate the Aesthetic score of each dataset

**2.6 caculate the diversity:**
   
caculate the diversity: `python ./evaluation/diversity.py`

caculate the novelty: `python ./evaluation/novelty.py` # cocodataset is no need to run this command# MMEvaluation
