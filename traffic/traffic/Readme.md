# **CS50AI Project3 Traffic**

<pr>I tried different layers for the traffic symbol data set from *gtrsb*. <br>
I tried one convolution map but it was relatively ineffective in both "relu", "sigmoid" and "softmax". I also tried the AveragePooling2D and MaxPooling2D and found that average yielded much better results.
For best results i found that 2 Convolution Layers were better, One (1) resulted in too much loss whereas Three (3) resulted in high calculation time. 2 convolution layers seemed ideal for both accuracy and calculation time.
</pr>

You can see the result on [Youtube](https://youtu.be/zxCT5pliYpI)

<video src="https://youtu.be/zxCT5pliYpI" controls ="controls">
</video>

