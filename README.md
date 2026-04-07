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

## 🏁 Status

✔ Database created
✔ Dataset loaded
✔ Chunking completed

Ready for **Step 4: Embeddings**
