package system

import (
	"os"
	"path"
	"runtime"
)

func GetLogDir() (loggingDir string, err error) {
	loggingDir = "/var/log/hyperglass"
	switch runtime.GOOS {
	case "windows":
		var userDir string
		userDir, err = os.UserHomeDir()
		if err != nil {
			return
		}
		loggingDir = path.Join(userDir, "AppData", "Local", "hyperglass", "logs")
	case "darwin":
		var userDir string
		userDir, err = os.UserHomeDir()
		if err != nil {
			return
		}
		loggingDir = path.Join(userDir, "Library", "Logs", "hyperglass")
	}
	return
}

func GetAppDir() (appDir string, err error) {
	appDir = "/etc/hyperglass"
	configDir, err := os.UserConfigDir()
	if err != nil {
		return
	}
	switch runtime.GOOS {
	case "windows":
		appDir = path.Join(configDir, "hyperglass")
	case "darwin":
		appDir = path.Join(configDir, "hyperglass")
	}
	return
}

func InitializeDirs() (err error) {
	logDir, err := GetLogDir()
	if err != nil {
		return
	}
	appDir, err := GetAppDir()
	if err != nil {
		return
	}
	_, err = os.Stat(logDir)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.Mkdir(logDir, 0755)
			if err != nil {
				return
			}
			return
		}
		return
	}
	_, err = os.Stat(appDir)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.Mkdir(appDir, 0755)
			if err != nil {
				return
			}
			return
		}
		return
	}
	return
}
