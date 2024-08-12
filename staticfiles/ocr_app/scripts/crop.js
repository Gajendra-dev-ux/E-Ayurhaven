// document.getElementById('upload-image').addEventListener('change', function (event) {
//     var image = document.getElementById('image');
//     var file = event.target.files[0];
//     var reader = new FileReader();

//     reader.onload = function (e) {
//         image.src = e.target.result;
//         image.style.display = 'block';

//         var cropper = new Cropper(image, {
//             aspectRatio: 1,
//             viewMode: 1,
//             autoCropArea: 1,
//         });

//         document.getElementById('crop-button').style.display = 'block';
//         document.getElementById('crop-button').addEventListener('click', function () {
//             var canvas = cropper.getCroppedCanvas({
//                 width: 300,
//                 height: 300,
//             });
//             canvas.toBlob(function (blob) {
//                 var url = URL.createObjectURL(blob);
//                 var croppedImage = new Image();
//                 croppedImage.src = url;
//                 document.body.appendChild(croppedImage);

//                 var reader = new FileReader();
//                 reader.readAsDataURL(blob);
//                 reader.onloadend = function () {
//                     document.getElementById('cropped_image_data').value = reader.result;
//                     document.getElementById('profile-form').submit();
//                 };
//             });
//         });
//     };

//     reader.readAsDataURL(file);
// });