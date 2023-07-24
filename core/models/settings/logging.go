package settings

import (
	"database/sql"

	"code.cloudfoundry.org/bytefmt"
	"github.com/thatmattlove/hyperglass/core/system"
	"gorm.io/gorm"
)

const (
	LOG_FORMAT_JSON string = "json"
	LOG_FORMAT_TEXT string = "text"
)

type Logging struct {
	gorm.Model
	Directory    string
	Format       string
	MaxSize      uint64
	EnableSyslog sql.NullBool `gorm:"default:false"`
	SyslogHost   *string
	SyslogPort   *int
	EnableHTTP   sql.NullBool `gorm:"default:false"`
	HTTPHost     *string
	SettingsID   uint
}

func SeedLogging() (logging Logging, err error) {
	loggingDir, err := system.GetLogDir()
	if err != nil {
		return
	}
	defaultLogSize, err := bytefmt.ToBytes("50MB")
	if err != nil {
		return
	}
	logging = Logging{
		Directory: loggingDir,
		Format:    LOG_FORMAT_TEXT,
		MaxSize:   defaultLogSize,
	}
	return
}
