import 'package:flutter/material.dart';

class AppTheme {
  // Color palette for AI companion theme
  static const Color primaryColor = Color(0xFF6366F1);
  static const Color secondaryColor = Color(0xFFEC4899);
  static const Color accentColor = Color(0xFF10B981);
  static const Color errorColor = Color(0xFFEF4444);
  static const Color warningColor = Color(0xFFF59E0B);

  // Neutral colors
  static const Color darkBlue = Color(0xFF1E293B);
  static const Color lightGray = Color(0xFFF8FAFC);
  static const Color mediumGray = Color(0xFF64748B);

  // Call interface colors
  static const Color callActiveColor = Color(0xFF10B981);
  static const Color callEndColor = Color(0xFFEF4444);
  static const Color callMutedColor = Color(0xFF6B7280);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.light,
      ),
      // fontFamily: 'Inter', // Commented out - using system default

      // App Bar Theme
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          // fontFamily: 'Inter', // Commented out - using system default
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: darkBlue,
        ),
        iconTheme: IconThemeData(color: darkBlue),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        color: Colors.white,
      ),

      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontFamily: 'Inter',
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Text Button Theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          textStyle: const TextStyle(
            fontFamily: 'Inter',
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),

      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: primaryColor,
        unselectedItemColor: mediumGray,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: TextStyle(
          fontFamily: 'Inter',
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
        unselectedLabelStyle: TextStyle(
          fontFamily: 'Inter',
          fontSize: 12,
          fontWeight: FontWeight.w400,
        ),
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.dark,
      ),
      // fontFamily: 'Inter', // Commented out - using system default

      // App Bar Theme
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          // fontFamily: 'Inter', // Commented out - using system default
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
        iconTheme: IconThemeData(color: Colors.white),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        color: const Color(0xFF1F2937),
      ),

      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            // fontFamily: 'Inter', // Commented out - using system default
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Color(0xFF1F2937),
        selectedItemColor: primaryColor,
        unselectedItemColor: mediumGray,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
    );
  }
}

// Custom text styles
class AppTextStyles {
  static const TextStyle headline1 = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 32,
    fontWeight: FontWeight.w700,
    color: AppTheme.darkBlue,
  );

  static const TextStyle headline2 = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: AppTheme.darkBlue,
  );

  static const TextStyle headline3 = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: AppTheme.darkBlue,
  );

  static const TextStyle bodyLarge = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: AppTheme.darkBlue,
  );

  static const TextStyle bodyMedium = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: AppTheme.darkBlue,
  );

  static const TextStyle bodySmall = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: AppTheme.mediumGray,
  );

  static const TextStyle caption = TextStyle(
    // fontFamily: 'Inter', // Using system default
    fontSize: 11,
    fontWeight: FontWeight.w400,
    color: AppTheme.mediumGray,
  );
}
