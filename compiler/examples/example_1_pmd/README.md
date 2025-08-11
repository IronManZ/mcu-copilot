# 格式转换指令
```
python ../../excel_converter.py -m excel-to-text -o example_1_smg.asm example_1_smg.xlsm
```

# 编译指令
```
python ../../zh5001_corrected_compiler.py example_1_smg.asm  
```

# 对比结果
```
diff example_1_smg.hex example_1_hex.hex
```