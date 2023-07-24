package settings

import "gorm.io/gorm"

type Settings struct {
	gorm.Model
	RequestTimeout   int    `gorm:"default:90"`
	OrganizationName string `gorm:"default:Beloved Hyperglass User"`
	UITitle          string `gorm:"default:hyperglass"`
	UIDescription    string `gorm:"Network Looking Glass"`
	Messages         []Message
	Logging          Logging
}

func Seed() (settings *Settings, err error) {
	logging, err := SeedLogging()
	if err != nil {
		return
	}
	settings = &Settings{
		Messages: SeedMessages(),
		Logging:  logging,
	}
	return
}
