CKEDITOR.editorConfig = function(config) {
    // Allow all content, but CKEditor will still filter some elements that are deemed unsafe.
    config.allowedContent = true;

    // Automatically wrap text in <p> tags
    config.autoParagraph = true;

    // Use the paste from Word plugin to clean up content pasted from Word
    config.extraPlugins = 'pastefromword';

    // Define custom allowed content rules
    config.extraAllowedContent = 'p(*){*}[*];';
};