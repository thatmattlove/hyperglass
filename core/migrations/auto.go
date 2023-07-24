package migrations

import (
	"errors"

	"github.com/thatmattlove/hyperglass/core/infrastructure/database"
	"github.com/thatmattlove/hyperglass/core/models"
	"github.com/thatmattlove/hyperglass/core/models/settings"
	"gorm.io/gorm"
)

func AutoMigrate() (err error) {
	db, err := database.New()
	if err != nil {
		return
	}
	err = db.DB.AutoMigrate(
		settings.Logging{},
		settings.Message{},
		models.Group{},
		models.Credential{},
		models.Device{},
		models.Proxy{},
	)
	if err != nil {
		return
	}
	if err = db.DB.AutoMigrate(&settings.Settings{}); err == nil && db.DB.Migrator().HasTable(&settings.Settings{}) {
		if err := db.DB.First(&settings.Settings{}).Error; errors.Is(err, gorm.ErrRecordNotFound) {
			s, err := settings.Seed()
			if err != nil {
				return err
			}
			tx := db.DB.Create(s)
			return tx.Error
		}
	}
	return
}
