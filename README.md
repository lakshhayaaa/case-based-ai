# Case-Based AI – Setup

---

## Step 1: Database Setup

### 1. Create database

```bash
psql -U postgres
```

```sql
CREATE DATABASE case_based_ai;
```

### 2. Run schema

```bash
psql -U postgres -d case_based_ai -f schema.sql
```

---

## 📥 Step 2: Load Dataset

### Run loader script

```bash
python load_dataset.py
```

---

## Step 3: Chunking

### Run chunking script

```bash
python -m utils.chunking
```


## ✅ Expected Output

* Cases loaded into database
* Cases split into multiple chunks
* Number of chunks > number of cases

---
## Step 4: Embeddings
```bash
pip3 install sentence-transformers
```
```bash
python3 -m rag_project.embedding_model
```

---

## Step 5: Store in VectorDB

```bash
pip3 install chromadb
```
```bash
python3 -m rag_project.vector_store
```


