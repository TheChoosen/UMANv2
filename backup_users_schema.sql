-- Sauvegarde du schéma de la table users
-- Date: {'Table': 'users', 'Create Table': "CREATE TABLE `users` (\n  `id` int NOT NULL AUTO_INCREMENT,\n  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,\n  `password` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,\n  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,\n  `is_admin` tinyint(1) DEFAULT '0',\n  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,\n  PRIMARY KEY (`id`),\n  UNIQUE KEY `username` (`username`),\n  UNIQUE KEY `email` (`email`),\n  KEY `idx_username` (`username`),\n  KEY `idx_email` (`email`)\n) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"}
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci