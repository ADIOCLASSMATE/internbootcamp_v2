python -m internbootcamp.utils.batch_data_generation \
    --bootcamp-registry internbootcamp/bootcamps/rectangle_count/configs/bootcamp_registry_rectangle_count.jsonl \
    --output-dir data/rectangle_count \
    --split-samples train:100,test:10 \
    --max-workers 64 \
    --log-level DEBUG \
    --continue-on-error \
    --no-tool \
    --no-interaction