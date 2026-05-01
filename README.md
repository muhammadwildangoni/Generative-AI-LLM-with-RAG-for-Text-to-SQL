# Generative-AI-LLM-with-RAG-for-Text-to-SQL
Project ini mengimplementasikan sistem Generative AI (LLM) dengan pendekatan Retrieval-Augmented Generation (RAG) untuk Text-to-SQL. Sistem ini memungkinkan pengguna mengubah pertanyaan dalam bahasa alami menjadi query SQL serta menghasilkan insight dari database relasional.

Pipeline yang dibangun meliputi proses schema extraction, pembuatan embedding menggunakan sentence-transformers, serta penyimpanan dalam vector database (Chroma) untuk melakukan retrieval context yang relevan. Context tersebut kemudian digunakan oleh LLM (Gemini) untuk menghasilkan query SQL yang akurat. Query yang dihasilkan dieksekusi pada database PostgreSQL, dan hasilnya diproses kembali menjadi insight dalam bahasa yang mudah dipahami.

Dataset yang digunakan pada project ini mengacu pada database Northwind PostgreSQL yang bersifat open-source.

Link database
https://github.com/pthom/northwind_psql
