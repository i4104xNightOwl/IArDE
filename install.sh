# INSTALL YAY HELPER
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si

# INSTALL XCB
sudo pacman -Syu python-pip libxcb xcb-util xcb-util-wm xcb-util-keysyms
sudo pacman -S sddm neovim kitty
