package api

import (
	"fmt"

	"github.com/gofiber/fiber/v2"
	"github.com/thatmattlove/hyperglass/core/controllers"
	"github.com/thatmattlove/hyperglass/core/infrastructure/database"
)

func Start() (err error) {
	db, err := database.New()
	if err != nil {
		return
	}
	settings := db.Settings()
	config := fiber.Config{
		ServerHeader: "hyperglass",
		AppName:      fmt.Sprintf("%s Looking Glass", settings.OrganizationName),
		Network:      "tcp",
	}
	app := fiber.New(config)
	app.Post("/api/query", controllers.QueryController)
	return app.Listen(":8080")
}
