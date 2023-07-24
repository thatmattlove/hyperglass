package cache

import (
	"os"
	"path"

	"go.etcd.io/bbolt"
)

type Cache struct {
	File    *os.File
	Backend *bbolt.DB
	Bucket  []byte
}

func (c *Cache) Get(key string) (value string, err error) {
	err = c.Transaction(func(db *bbolt.DB) error {
		err = db.View(func(tx *bbolt.Tx) error {
			b := tx.Bucket(c.Bucket)
			v := b.Get([]byte(key))
			value = string(v)
			return nil
		})
		return err
	})
	return
}

func (c *Cache) Set(key, value string) (err error) {
	return c.Transaction(func(db *bbolt.DB) error {
		return db.Update(func(tx *bbolt.Tx) error {
			b := tx.Bucket(c.Bucket)
			return b.Put([]byte(key), []byte(value))
		})
	})
}

func (c *Cache) Transaction(cb func(db *bbolt.DB) error) (err error) {
	db, err := bbolt.Open(c.File.Name(), 0666, nil)
	if err != nil {
		return
	}

	defer db.Close()
	defer c.File.Close()
	return cb(db)
}

func (c *Cache) Destroy(name string) (err error) {
	err = c.Backend.Close()
	if err != nil {
		return
	}
	err = os.Remove(c.File.Name())
	return
}

func New(name string) (c *Cache, err error) {
	cacheDir, err := os.MkdirTemp("", "hyperglass-cache-*")
	if err != nil {
		return
	}
	cacheFile, err := os.Create(path.Join(cacheDir, "hyperglass.cache"))
	if err != nil {
		return
	}
	db, err := bbolt.Open(cacheFile.Name(), 0666, nil)
	if err != nil {
		return
	}
	defer db.Close()
	defer cacheFile.Close()
	bucket := []byte(name)
	err = db.Update(func(tx *bbolt.Tx) (err error) {
		_, err = tx.CreateBucket(bucket)
		return
	})
	if err != nil {
		return
	}
	c = &Cache{
		Backend: db,
		File:    cacheFile,
		Bucket:  bucket,
	}
	return
}
