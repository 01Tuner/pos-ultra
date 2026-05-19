/** Returns true when running on an Android device. */
export function isAndroid() {
	return /android/i.test(navigator.userAgent)
}
