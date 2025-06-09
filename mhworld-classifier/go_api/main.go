// go_api/main.go
package main

import (
	"log"
	"os"
	"time"

	"go_api/handlers" // Importa o pacote de handlers
	"go_api/service"  // Importa o pacote de serviços

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	gin.SetMode(gin.ReleaseMode) // Modo de produção para Gin
	router := gin.Default()

	// Configuração CORS: permite requisições do Streamlit (localhost:8501)
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:8501"},
		AllowMethods:     []string{"POST", "GET", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Instancia o serviço de ML
	mlService := service.NewMLService("ml_model/src/predict_model.py")

	// Registra a rota POST /classify, passando a instância do serviço
	router.POST("/classify", handlers.ClassifyHandler(mlService))

	// Define a porta da API (variável de ambiente PORT ou 8080 padrão)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("API Go iniciada e escutando na porta :%s", port)
	log.Fatal(router.Run(":" + port)) // Inicia o servidor HTTP
}
