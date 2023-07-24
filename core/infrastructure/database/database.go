package database

import (
	"os"
	"path"

	"github.com/thatmattlove/hyperglass/core/models/settings"
	"github.com/thatmattlove/hyperglass/core/system"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type IDB struct {
	File string
	DB   *gorm.DB
}

func (idb *IDB) Settings() (settings *settings.Settings) {
	idb.DB.Limit(1).Find(&settings)
	return
}

func New() (idb *IDB, err error) {
	appDir, err := system.GetAppDir()
	if err != nil {
		return
	}
	dbFile := path.Join(appDir, "hyperglass.db")
	if _, err = os.Stat(dbFile); os.IsNotExist(err) {
		_, err = os.Create(dbFile)
		if err != nil {
			return
		}
	}
	db, err := gorm.Open(sqlite.Open(dbFile), &gorm.Config{
		DisableForeignKeyConstraintWhenMigrating: true,
	})
	idb = &IDB{
		File: dbFile,
		DB:   db,
	}
	return
}
