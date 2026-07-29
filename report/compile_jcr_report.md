# 《密码学报》模板版报告编译说明

主文件：

```text
report/main.tex
```

该文件已经适配《密码学报》中文 LaTeX 模板，依赖文件均已放在 `report/` 目录：

- `jcr.cls`
- `jcr.cfg`
- `mfirstuc.sty`
- `references.bib`

推荐使用 XeLaTeX 编译：

```bash
cd report
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

当前环境已通过 MiKTeX 提供 `xelatex`，并已生成最终 PDF：

```text
output/pdf/现代密码学课程报告_曾嘉祺_中文图表版.pdf
```

提交前建议修改：

1. 作者姓名和邮箱已替换为曾嘉祺、`20251010015@mail.gdufs.edu.cn`。
2. DOI、卷期、期号、收稿日期、定稿日期和页码范围等期刊占位字段已删除。
3. 编译后检查首页标题、摘要、表格、算法和参考文献是否溢出。
4. `\authorinfo` 之后的作者简介部分已删除，正文不包含学号、班级或专业信息。
