from transformers.file_utils import hf_bucket_url, cached_path

src = 'zh'  # source language
trg = 'en'  # target language
#pretrained_model_name = f'Helsinki-NLP/opus-mt-{src}-{trg}'
pretrained_model_name = f'distilgpt'
# pretrained_model_name = 'DeepPavlov/rubert-base-cased'
archive_file = hf_bucket_url(
    pretrained_model_name,
    filename='pytorch_model.bin',
    use_cdn=True,
)
resolved_archive_file = cached_path(archive_file)

print(resolved_archive_file)