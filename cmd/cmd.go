package cmd

import (
	"github.com/k0kubun/pp/v3"
	"github.com/spf13/cobra"
	"github.com/thatmattlove/hyperglass/core/api"
	"github.com/thatmattlove/hyperglass/core/infrastructure/database"
	"github.com/thatmattlove/hyperglass/core/migrations"
	"github.com/thatmattlove/hyperglass/core/system"
)

func start(cmd *cobra.Command, args []string) {
	cobra.CheckErr(api.Start())
}

func settings(cmd *cobra.Command, args []string) {
	db, err := database.New()
	cobra.CheckErr(err)
	settings := db.Settings()
	pp.Print(settings)
}

func initializeCmd() {
	err := system.InitializeDirs()
	cobra.CheckErr(err)
	err = migrations.AutoMigrate()
	cobra.CheckErr(err)
}

func Main() error {
	initializeCmd()
	root := &cobra.Command{
		Use:   "hyperglass",
		Short: "hyperglass is the network looking glass that tries to make the internet better.",
	}
	root.AddCommand(&cobra.Command{
		Use:   "start",
		Short: "Start hyperglass",
		Run:   start,
	})
	root.AddCommand(&cobra.Command{
		Use:   "settings",
		Short: "Show hyperglass settings",
		Run:   settings,
	})
	return root.Execute()
}
