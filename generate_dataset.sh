for tp in h v b r hr
do
    python3 generate_samples.py --type $tp
done

python3 generate_samples.py --type h --index_shuffle